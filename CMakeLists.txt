cmake_minimum_required(VERSION 3.20)
project(nwproto_reference CXX)

# ---------------------------------------------------------------------------
# Reference GridMate build (NWLY chunk T4)
#
# Carve-out of AzCore + GridMate from the Lumberyard fork, bypassing Waf.
# Recipe proven by the T4 toolchain probe:
#   -std=c++17        (NOT c++14 - Waf's -std=c++1y flag was stale vs the code)
#   -include utility  (std::exchange on libstdc++ 16)
#   TypeInfo.h patch  (false_v<T> -> false_v<>, committed in the fork)
#   system clang 22   (no /opt/llvm14 needed)
# ---------------------------------------------------------------------------

set(LY_ROOT "$ENV{HOME}/Documents/lumberyard/dev/Code/Framework"
    CACHE PATH "Lumberyard dev/Code/Framework directory")

set(AZCORE_DIR   "${LY_ROOT}/AzCore")
set(GRIDMATE_DIR "${LY_ROOT}/GridMate")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Not -Werror: this is 2019 code on a 2026 toolchain, warnings are expected.
add_compile_options(
    -Wno-error
    -Wno-deprecated-literal-operator
    -Wno-deprecated-declarations
    -Wno-unused-parameter
    -Wno-unused-variable
    -include utility          # std::exchange for AzCore/std/utils.h
)

# ---------------------------------------------------------------------------
# AzCore
# ---------------------------------------------------------------------------
file(GLOB_RECURSE AZCORE_SOURCES CONFIGURE_DEPENDS "${AZCORE_DIR}/AzCore/*.cpp")
file(GLOB_RECURSE AZCORE_LINUX_SOURCES CONFIGURE_DEPENDS
     "${AZCORE_DIR}/Platform/Linux/*.cpp")

add_library(azcore STATIC ${AZCORE_SOURCES} ${AZCORE_LINUX_SOURCES})

target_include_directories(azcore PUBLIC
    "${AZCORE_DIR}"                  # so <AzCore/...> resolves
    "${AZCORE_DIR}/Platform/Linux"   # so <AzCore/AzCore_Traits_Platform.h> resolves
)

find_package(Threads REQUIRED)
target_link_libraries(azcore PUBLIC Threads::Threads ${CMAKE_DL_LIBS})

# ---------------------------------------------------------------------------
# GridMate
# ---------------------------------------------------------------------------
file(GLOB_RECURSE GRIDMATE_SOURCES CONFIGURE_DEPENDS
     "${GRIDMATE_DIR}/GridMate/*.cpp")
file(GLOB_RECURSE GRIDMATE_LINUX_SOURCES CONFIGURE_DEPENDS
     "${GRIDMATE_DIR}/Platform/Linux/*.cpp")

add_library(gridmate STATIC ${GRIDMATE_SOURCES} ${GRIDMATE_LINUX_SOURCES})

target_include_directories(gridmate PUBLIC
    "${GRIDMATE_DIR}"
    "${GRIDMATE_DIR}/Platform/Linux"
)

# SecureSocketDriver.cpp calls OpenSSL directly (confirmed in STATE section 7).
find_package(OpenSSL REQUIRED)
target_link_libraries(gridmate PUBLIC azcore OpenSSL::SSL OpenSSL::Crypto)

# Amazon never defined this for Linux, so the secure path defaults off.
# Turn it on explicitly - expect Linux-specific DTLS bugs (STATE section 7).
target_compile_definitions(gridmate PUBLIC
    AZ_TRAIT_GRIDMATE_TEST_WITH_SECURE_SOCKET_DRIVER=1
)

# ---------------------------------------------------------------------------
# carrier_probe - the T4 milestone: two Carriers connecting locally
# ---------------------------------------------------------------------------
add_executable(carrier_probe
    "${CMAKE_CURRENT_SOURCE_DIR}/carrier_probe.cpp"
    "${GRIDMATE_DIR}/Tests/Certificates.cpp"   # g_untrustedCertPEM / PrivateKeyPEM
)
target_link_libraries(carrier_probe PRIVATE gridmate)
