// NWLY / T4 step 4 -- minimal two-Carrier plaintext localhost session.
//
// Path B from T4_PROMPT: no gtest, no AzTest, just a main() that stands up two
// GridMate Carriers on loopback, connects one to the other, exchanges a payload
// both ways, and exits 0 on success.
//
// This is the milestone: a stock GridMate Carrier session under our control,
// whose wire traffic can be captured and diffed against retail.
//
// Build (from dev/Code/Framework, archives from build_gridmate.sh):
//   clang++ -std=c++17 -include utility -fdelayed-template-parsing -w \
//     -DDTLS1_RT_HEARTBEAT=24 \
//     -I AzCore -I AzCore/Platform/Linux -I GridMate -I GridMate/Platform/Linux \
//     nwly_carrier_probe.cpp <out>/libgridmate.a <out>/libazcore.a \
//     -lssl -lcrypto -lpthread -ldl -o <out>/carrier_probe
//
// Capture while it runs:
//   sudo tcpdump -i lo -w carrier_plaintext.pcap 'udp and (port 4427 or port 4428)'

#include <AzCore/Memory/SystemAllocator.h>
#include <AzCore/Memory/OSAllocator.h>
#include <AzCore/std/parallel/thread.h>
#include <AzCore/std/chrono/chrono.h>

#include <GridMate/GridMate.h>
#include <GridMate/Carrier/Carrier.h>
#include <GridMate/Carrier/DefaultHandshake.h>
#include <GridMate/Carrier/SocketDriver.h>

#include <cstdio>
#include <cstring>

using namespace GridMate;

namespace
{
    const unsigned short kServerPort = 4428;
    const unsigned short kClientPort = 4427;
    const char* kPayload = "NWLY carrier probe payload";

    // Catches connection events so we learn the ConnectionIDs the two sides
    // assign. Without this there is no way to address a Send().
    class Callbacks : public CarrierEventBus::Handler
    {
    public:
        Carrier* m_carrier = nullptr;
        ConnectionID m_connectionID = InvalidConnectionID;
        ConnectionID m_incomingConnectionID = InvalidConnectionID;
        bool m_failed = false;
        const char* m_label = "?";

        void Activate(Carrier* c, const char* label)
        {
            m_carrier = c;
            m_label = label;
            CarrierEventBus::Handler::BusConnect(c->GetGridMate());
        }
        ~Callbacks() override { CarrierEventBus::Handler::BusDisconnect(); }

        void OnIncomingConnection(Carrier* c, ConnectionID id) override
        {
            if (c != m_carrier) return;
            m_incomingConnectionID = id;
            std::printf("  [%s] incoming connection\n", m_label);
        }
        void OnConnectionEstablished(Carrier* c, ConnectionID id) override
        {
            if (c != m_carrier) return;
            m_connectionID = id;
            std::printf("  [%s] connection established\n", m_label);
        }
        void OnFailedToConnect(Carrier* c, ConnectionID, CarrierDisconnectReason r) override
        {
            if (c != m_carrier) return;
            m_failed = true;
            std::printf("  [%s] FAILED TO CONNECT, reason %d\n", m_label, (int)r);
        }
        void OnDisconnect(Carrier* c, ConnectionID, CarrierDisconnectReason r) override
        {
            if (c != m_carrier) return;
            std::printf("  [%s] disconnected, reason %d\n", m_label, (int)r);
        }
        void OnDriverError(Carrier* c, ConnectionID, const DriverError& e) override
        {
            if (c != m_carrier) return;
            std::printf("  [%s] DRIVER ERROR %d\n", m_label, (int)e.m_errorCode);
        }
        void OnSecurityError(Carrier* c, ConnectionID, const SecurityError& e) override
        {
            if (c != m_carrier) return;
            std::printf("  [%s] SECURITY ERROR %d\n", m_label, (int)e.m_errorCode);
        }
    };
}

int main()
{
    std::printf("NWLY carrier probe -- two Carriers, plaintext, loopback\n");

    // ---- AzCore bootstrap -------------------------------------------------
    // A standalone binary gets none of what ComponentApplication normally does,
    // so the SystemAllocator must be stood up by hand before anything else.
    // OSAllocator underpins everything, including the azmalloc below that
    // supplies SystemAllocator's heap. AzTest's environment normally creates it;
    // a standalone binary must do it first or the first azmalloc segfaults
    // dereferencing a null allocator.
    AZ::AllocatorInstance<AZ::OSAllocator>::Create();

    const unsigned int memorySize = 64 * 1024 * 1024;
    AZ::SystemAllocator::Descriptor sysAllocDesc;
    sysAllocDesc.m_heap.m_numFixedMemoryBlocks = 1;
    sysAllocDesc.m_heap.m_fixedMemoryBlocksByteSize[0] = memorySize;
    void* allocatorBuffer = azmalloc(memorySize,
                                     sysAllocDesc.m_heap.m_memoryBlockAlignment,
                                     AZ::OSAllocator);
    sysAllocDesc.m_heap.m_fixedMemoryBlocks[0] = allocatorBuffer;
    AZ::AllocatorInstance<AZ::SystemAllocator>::Create(sysAllocDesc);

    GridMateDesc desc;
    desc.m_allocatorDesc.m_custom = &AZ::AllocatorInstance<AZ::SystemAllocator>::Get();
    IGridMate* gridMate = GridMateCreate(desc);
    if (!gridMate) { std::printf("FAIL: GridMateCreate returned null\n"); return 1; }

    // Carrier allocates from GridMateAllocatorMP. StartMultiplayerService would
    // normally create it; we are not starting a session service, so do it here.
    {
        GridMateAllocatorMP::Descriptor mpDesc;
        mpDesc.m_custom = &AZ::AllocatorInstance<GridMateAllocator>::Get();
        AZ::AllocatorInstance<GridMateAllocatorMP>::Create(mpDesc);
    }
    std::printf("  gridmate up\n");

    bool clientGot = false, serverGot = false;
    int rc = 0;

    // Everything that touches the EBus lives in this scope. The Callbacks
    // destructors call BusDisconnect(), which touches the EBus context -- so
    // they MUST run before GridMateDestroy and the allocator teardown below.
    // Leaving them as plain locals of main() is a use-after-free.
    {
    // ---- two carriers on loopback ----------------------------------------
    CarrierDesc serverDesc, clientDesc;
    serverDesc.m_port = kServerPort;
    clientDesc.m_port = kClientPort;
    // Disconnect detection adds keepalive traffic that muddies a first capture.
    serverDesc.m_enableDisconnectDetection = false;
    clientDesc.m_enableDisconnectDetection = false;

    Carrier* serverCarrier = DefaultCarrier::Create(serverDesc, gridMate);
    Carrier* clientCarrier = DefaultCarrier::Create(clientDesc, gridMate);
    if (!serverCarrier || !clientCarrier)
    {
        std::printf("FAIL: DefaultCarrier::Create returned null\n");
        return 1;
    }

    Callbacks serverCB, clientCB;
    serverCB.Activate(serverCarrier, "server");
    clientCB.Activate(clientCarrier, "client");
    std::printf("  server on %u, client on %u\n", kServerPort, kClientPort);

    const size_t payloadLen = std::strlen(kPayload);
    char buffer[1500];
    const int maxUpdates = 2000;
    int n = 0;

    for (; n < maxUpdates; ++n)
    {
        if (n == 0)
        {
            if (clientCarrier->Connect("127.0.0.1", kServerPort) == InvalidConnectionID)
            {
                std::printf("FAIL: Connect returned InvalidConnectionID\n");
                rc = 1; break;
            }
            std::printf("  connect issued\n");
        }
        else if (n == 200)
        {
            if (clientCB.m_connectionID == InvalidConnectionID ||
                serverCB.m_incomingConnectionID == InvalidConnectionID)
            {
                std::printf("FAIL: not connected after 200 updates\n");
                rc = 1; break;
            }
            serverCarrier->Send(kPayload, (unsigned int)payloadLen, serverCB.m_incomingConnectionID);
            clientCarrier->Send(kPayload, (unsigned int)payloadLen, clientCB.m_connectionID);
            std::printf("  payload sent both ways\n");
        }
        else if (n > 200)
        {
            Carrier::ReceiveResult r =
                clientCarrier->Receive(buffer, sizeof(buffer), clientCB.m_connectionID);
            if (r.m_state == Carrier::ReceiveResult::RECEIVED && r.m_numBytes == payloadLen)
                clientGot = std::strncmp(kPayload, buffer, r.m_numBytes) == 0;

            r = serverCarrier->Receive(buffer, sizeof(buffer), serverCB.m_incomingConnectionID);
            if (r.m_state == Carrier::ReceiveResult::RECEIVED && r.m_numBytes == payloadLen)
                serverGot = std::strncmp(kPayload, buffer, r.m_numBytes) == 0;

            if (clientGot && serverGot) break;
        }

        if (clientCB.m_failed || serverCB.m_failed) { std::printf("FAIL: connect failed\n"); rc = 1; break; }

        serverCarrier->Update();
        clientCarrier->Update();
        AZStd::this_thread::sleep_for(AZStd::chrono::milliseconds(10));
    }

    std::printf("  client received: %s\n", clientGot ? "yes" : "NO");
    std::printf("  server received: %s\n", serverGot ? "yes" : "NO");
    std::printf("  updates used: %d of %d\n", n, maxUpdates);

    DefaultCarrier::Destroy(clientCarrier);
    DefaultCarrier::Destroy(serverCarrier);
    }   // Callbacks destroyed here, while the EBus context is still alive.

    AZ::AllocatorInstance<GridMateAllocatorMP>::Destroy();
    GridMateDestroy(gridMate);
    AZ::AllocatorInstance<AZ::SystemAllocator>::Destroy();
    azfree(allocatorBuffer, AZ::OSAllocator);
    AZ::AllocatorInstance<AZ::OSAllocator>::Destroy();

    const bool ok = (rc == 0) && clientGot && serverGot;
    std::printf("%s\n", ok ? "PASS -- plaintext Carrier session established both ways"
                           : "FAIL -- payload did not round-trip");
    return ok ? 0 : 1;
}
