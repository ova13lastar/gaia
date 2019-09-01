import gaia.config as settings

def test_app_config():
    app = settings.App()
    assert isinstance(app, settings.App)
    assert app.config("LOCK_EXTENSION") == ".lock"
    assert app.config("CONF_DIR_NAME") == "conf"

# def test_init():
#     c = config.ConfigLog()
#     assert isinstance(c)
