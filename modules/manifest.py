# Include standard frozen modules
include("$(MPY_DIR)/extmod/asyncio/manifest.py")  # noqa: F821

# Include any python files in the modules/ directory
freeze("$(MANIFEST_DIR)")  # noqa: F821

# Include LVGL helper modules if they exist in the binding submodule
# (Adjust paths if necessary based on version)
# freeze("$(PORT_DIR)/../../../../submodules/lv_binding_micropython/lib")
