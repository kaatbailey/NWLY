# P2 scan report

- target: `/home/kaatlev/Documents/nwly-pin/22469132/Bin64/NewWorld.exe`
- size: 179204176 bytes
- image base: `0x140000000`
- FileDescriptorProto blobs recovered: **3**
- total messages: **32**
- total service blocks: **0**

## Registered .proto files

| # | path | package | VA | size | msgs | svcs | conf | signature (first 16B) |
|---|---|---|---|---|---|---|---|---|
| 0 | `campfire_event_default.proto` | `` | `0x1486f5b60` | 1407 | 4 | 0 | exact | `0a1c63616d70666972655f6576656e74` |
| 1 | `google/protobuf/empty.proto` | `google.protobuf` | `0x1495ab7c0` | 190 | 1 | 0 | exact | `0a1b676f6f676c652f70726f746f6275` |
| 2 | `google/protobuf/descriptor.proto` | `google.protobuf` | `0x1495b3330` | 6028 | 27 | 0 | exact | `0a20676f6f676c652f70726f746f6275` |

## Service blocks (both directions in one place)

**None.** No `service` block is present in any recovered descriptor. P2 prediction 3 is FALSIFIED if this holds on the retail binary: there is no single RPC interface listing both directions.

## Server->client candidates (OI-H2-3)

**None found by name.** No message name ends in Result, Response, Notification, Event, Update or Snapshot.

## Diagnostics -- serialization shape

| string | count |
|---|---|
| `InternalAddGeneratedFile` | 0 |
| `AddDescriptors` | 0 |
| `descriptor_table` | 0 |
| `google/protobuf/descriptor.proto` | 2 |
| `google::protobuf::Reflection` | 1 |
| `google::protobuf::MessageLite` | 0 |
| `google::protobuf::DescriptorPool` | 0 |
| `AmazonSerializableWebServiceRequest` | 1 |
| `Aws::Utils::Json::JsonValue` | 1 |
| `Aws::Utils::Json::JsonView` | 0 |
| `SerializePayload` | 0 |
| `JavelinGatewayService` | 20 |
| `application/json` | 236 |
| `application/x-protobuf` | 0 |
| `application/octet-stream` | 0 |
| `ReplicaChunk` | 23 |
| `InitializeReplicatedFields` | 94 |
| `DataSetBase` | 0 |
| `Marshaler` | 0 |

Reading: high `JsonValue`/`JsonView`/`AmazonSerializableWebServiceRequest` counts with an `application/json` content type indicate the AWS SDK path is JSON, not protobuf -- which would mean the Javelin Gateway models are NOT the protobuf choke point and protobuf serves some other subsystem.

