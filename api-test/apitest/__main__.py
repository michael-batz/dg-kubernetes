import kubernetes


def main():
    # create configuration and client
    config = kubernetes.client.Configuration()
    config.api_key_prefix['authorization'] = 'Bearer'
    config.api_key['authorization'] = 'xyz'
    config.host = 'https://localhost'
    config.verify_ssl = False
    client = kubernetes.client.ApiClient(config)

    # test: get kubernetes nodes
    api = kubernetes.client.CoreV1Api(client)
    result = api.list_node()
    print(result)

    # apply yaml file
    # this seems to create only new objects but does not update existing ones?
    result = kubernetes.utils.create_from_yaml(client, 'test.yml')
    print(result)

if __name__ == '__main__':
    main()
