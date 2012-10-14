from run_step import setup_db


def pytest_generate_tests(metafunc):
    if 'step' in metafunc.funcargnames:  # pragma: no branch
        metafunc.parametrize('step', range(1, 5))
    if 'endpoint' in metafunc.funcargnames:  # pragma: no branch
        metafunc.parametrize('endpoint', ('/', '/posts/1', '/posts/2', '/posts/3'))


def teardown_db(db):
    db.drop_all()


def test_step_equal_results(step, endpoint):
    import step1 as first
    step = __import__('step%i' % step)

    setup_db(first)
    first_response = first.app.test_client().get("%s?format=json" % endpoint)
    teardown_db(first.db)

    setup_db(step)
    step_response = step.app.test_client().get("%s?format=json" % endpoint)
    teardown_db(step.db)

    assert first_response.status_code == step_response.status_code
    assert first_response.data == step_response.data
