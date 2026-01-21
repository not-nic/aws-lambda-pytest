"""
Can also just use load_lambda here and provide a module_name manually like 'lambda_ssm'

Additionally, if it contains methods other than "lambda_handler", like "foo", "bar",
this would still work as the module is loaded and ready to use here.
"""

def test_lambda_ssm_reader(load_lambda, module_name, mock_ssm_client):
    module = load_lambda(module_name)

    response = module.lambda_handler({}, {})
    assert response["value"] == "ssm-value"