#!/usr/bin/env python3
"""Apply idempotent libadrenotools/Turnip integration to the pinned ReXGlue SDK."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-turnip.py /path/to/rexglue-sdk")
root = Path(sys.argv[1]).resolve()
changes = [
("include/rex/platform/dynlib.h",
"  void Close();\n  explicit operator bool() const { return handle_ != nullptr; }",
"""  void Close();
  // Adopt a handle opened by libadrenotools; DynamicLibrary owns it afterwards.
  void Adopt(void* handle) { Close(); handle_ = handle; }
  explicit operator bool() const { return handle_ != nullptr; }""","DynamicLibrary::Adopt"),
("src/ui/vulkan/vulkan_instance.cpp",
"""#if REX_PLATFORM_MAC
#include "vulkan_moltenvk.h"
#endif""",
"""#if REX_PLATFORM_MAC
#include "vulkan_moltenvk.h"
#endif
#if REX_PLATFORM_ANDROID && defined(REX_HAS_ADRENOTOOLS)
#include <cstdlib>
#include <dlfcn.h>
#include <adrenotools/driver.h>
#endif""","adrenotools headers"),
("src/ui/vulkan/vulkan_instance.cpp",
'REXCVAR_DEFINE_BOOL(vulkan_log_debug_messages, true, "UI/Vulkan", "Log Vulkan debug messages");',
'''REXCVAR_DEFINE_BOOL(vulkan_log_debug_messages, true, "UI/Vulkan", "Log Vulkan debug messages");
#if REX_PLATFORM_ANDROID
REXCVAR_DEFINE_STRING(android_gpu_driver_dir, "", "UI/Vulkan", "Private app directory containing a custom Vulkan driver").lifecycle(rex::cvar::Lifecycle::kInitOnly);
REXCVAR_DEFINE_STRING(android_gpu_driver_name, "", "UI/Vulkan", "Custom Vulkan driver library filename; empty uses system driver").lifecycle(rex::cvar::Lifecycle::kInitOnly);
REXCVAR_DEFINE_STRING(android_native_lib_dir, "", "UI/Vulkan", "Android nativeLibraryDir containing adrenotools hook libraries").lifecycle(rex::cvar::Lifecycle::kInitOnly);
REXCVAR_DEFINE_STRING(android_tmp_dir, "", "UI/Vulkan", "Writable temporary directory for adrenotools on legacy Android").lifecycle(rex::cvar::Lifecycle::kInitOnly);
REXCVAR_DEFINE_STRING(android_turnip_debug, "", "UI/Vulkan", "Optional Mesa TU_DEBUG options").lifecycle(rex::cvar::Lifecycle::kInitOnly);
#endif''',"Android Vulkan cvars"),
("src/ui/vulkan/vulkan_instance.cpp",
'''#else
  loader_loaded = vulkan_instance->loader_.Load(platform::lib_names::kVulkanLoader);
  if (!loader_loaded) {''',
'''#else
#if REX_PLATFORM_ANDROID && defined(REX_HAS_ADRENOTOOLS)
  {
    const std::string& name = REXCVAR_GET(android_gpu_driver_name);
    REXLOG_INFO("[RECVX-VK-DRIVER] custom selection: name='{}' dir='{}' hooks='{}' tmp='{}'", name, REXCVAR_GET(android_gpu_driver_dir), REXCVAR_GET(android_native_lib_dir), REXCVAR_GET(android_tmp_dir));
    if (!name.empty()) {
      std::string dir = REXCVAR_GET(android_gpu_driver_dir);
      if (!dir.empty() && dir.back() != '/') dir += '/';
      const std::string& hooks = REXCVAR_GET(android_native_lib_dir);
      const std::string& tmp = REXCVAR_GET(android_tmp_dir);
      const std::string& debug = REXCVAR_GET(android_turnip_debug);
      if (!debug.empty()) { setenv("TU_DEBUG", debug.c_str(), 1); REXLOG_INFO("Turnip TU_DEBUG={}", debug); }
      void* handle = adrenotools_open_libvulkan(RTLD_NOW, ADRENOTOOLS_DRIVER_CUSTOM,
          tmp.empty() ? nullptr : tmp.c_str(), hooks.c_str(), dir.c_str(), name.c_str(),
          nullptr, nullptr);
      if (handle) {
        vulkan_instance->loader_.Adopt(handle);
        loader_loaded = true;
        REXLOG_INFO("Loaded custom Vulkan driver through libadrenotools: {}{}", dir, name);
      } else {
        REXLOG_WARN("Could not load custom Vulkan driver {}{}; falling back to system Vulkan", dir, name);
      }
    }
  }
  if (!loader_loaded) loader_loaded = vulkan_instance->loader_.Load(platform::lib_names::kVulkanLoader);
#else
  loader_loaded = vulkan_instance->loader_.Load(platform::lib_names::kVulkanLoader);
#endif
  if (!loader_loaded) {''',"custom driver load with system fallback"),
("src/ui/vulkan/vulkan_device.cpp",
'''  ifn.vkGetPhysicalDeviceProperties(physical_device, &properties);''',
'''  ifn.vkGetPhysicalDeviceProperties(physical_device, &properties);
  REXLOG_INFO(
      "[RECVX-VK-DRIVER] device='{}' vendor=0x{:04X} device_id=0x{:04X} api={}.{}.{} driver_version=0x{:08X}",
      properties.deviceName, properties.vendorID, properties.deviceID,
      VK_VERSION_MAJOR(properties.apiVersion), VK_VERSION_MINOR(properties.apiVersion),
      VK_VERSION_PATCH(properties.apiVersion), properties.driverVersion);''',
"explicit physical-device identity diagnostics"),
("src/ui/CMakeLists.txt",
"target_link_libraries(rexui PRIVATE utf8cpp)",
"""target_link_libraries(rexui PRIVATE utf8cpp)
if(ANDROID AND TARGET adrenotools)
    target_link_libraries(rexui PUBLIC adrenotools android log)
    target_compile_definitions(rexui PRIVATE REX_HAS_ADRENOTOOLS=1)
endif()""","link adrenotools"),
("thirdparty/CMakeLists.txt",
"add_subdirectory(sdl3)",
"""add_subdirectory(sdl3)
if(ANDROID AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/libadrenotools/CMakeLists.txt")
    add_subdirectory(libadrenotools)
endif()""","build libadrenotools"),
]
pending = {}
for rel, old, new, label in changes:
    p = root / rel
    if not p.is_file():
        raise SystemExit(f"[turnip] missing SDK file: {rel}")
    # Multiple patches target the same file. Always apply the next patch
    # to the in-memory version so earlier changes are never overwritten.
    src = pending.get(rel)
    if src is None:
        src = p.read_text(encoding="utf-8")
    if new in src:
        pending[rel] = src
    elif src.count(old) == 1:
        pending[rel] = src.replace(old, new, 1)
    else:
        raise SystemExit(
            f"[turnip] {label}: anchor count {src.count(old)} in {rel}; no files written"
        )
for rel, src in pending.items():
    (root / rel).write_text(src, encoding="utf-8")
# Verify using stable markers rather than requiring the entire inserted block
# to remain byte-identical (formatting/line-ending changes are harmless).
markers = {
    "include/rex/platform/dynlib.h": "void Adopt(void* handle)",
    "src/ui/vulkan/vulkan_instance.cpp": "#include <adrenotools/driver.h>",
    "src/ui/CMakeLists.txt": "REX_HAS_ADRENOTOOLS=1",
    "thirdparty/CMakeLists.txt": "add_subdirectory(libadrenotools)",
}
for rel, marker in markers.items():
    if marker not in (root / rel).read_text(encoding="utf-8"):
        raise SystemExit(f"[turnip] post-patch verification failed: {marker} missing in {rel}")
print("[turnip] libadrenotools SDK integration applied and verified")
print("[turnip] custom driver is opt-in; system Vulkan remains the fallback")
