def pytest_addoption(parser):
    parser.addoption(
        "--nogen",
        default=False,
        action="store_true",
        help="run tests on pregenerated model",
    )
