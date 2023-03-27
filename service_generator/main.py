"""백엔드 코파일럿"""
from my_ai import require_json, require_json_v2, ContextStore, schema_dumps


def validate_domains(domains):
    """도메인 검증"""
    print(isinstance(domains, list))
    print(type(domains))
    if not isinstance(domains, list):
        raise Exception("domains should be array of object")
    for domain in domains:
        if not isinstance(domain, dict):
            raise Exception("domain should be object")
        if "name" not in domain:
            raise Exception("domain should have name")
        if "responsibility" not in domain:
            raise Exception("domain should have responsibility")
        if "interfaces" not in domain:
            raise Exception("domain should have interfaces")
        if not isinstance(domain["interfaces"], list):
            raise Exception("interfaces should be array of object")
        for interface in domain["interfaces"]:
            if not isinstance(interface, dict):
                raise Exception("interface should be object")
            if "name" not in interface:
                raise Exception("interface should have name")
            if "responsibility" not in interface:
                raise Exception("interface should have responsibility")
        if "entities" not in domain:
            raise Exception("domain should have entities")
        if not isinstance(domain["entities"], list):
            raise Exception("entities should be array of object")
        for entity in domain["entities"]:
            if not isinstance(entity, dict):
                raise Exception("entity should be object")
            if "name" not in entity:
                raise Exception("entity should have name")
            if "responsibility" not in entity:
                raise Exception("entity should have responsibility")
            if "schema" not in entity:
                raise Exception("entity should have schema")
            if not isinstance(entity["schema"], dict):
                raise Exception("schema should be object")
    return domains


def define_domains(service_description, language, framework):
    """도메인 정의"""
    template_prompt = f"""I'm trying to make a service like this
"{service_description}"

with {language} and {framework}

Divide this service by domain.
"""

    max_retry = 3
    retry = 0
    while True:
        try:
            print("try to define domains")
            prompt, domains = require_json_v2(
                template_prompt,
                [
                    {
                        "name": "name of domain",
                        "responsibility": "responsibility of the domain",
                        "interfaces": [
                            {
                                "name": "name of interface",
                                "responsibility": "responsibility",
                            }
                        ],
                        "entities": [
                            {
                                "name": "name of entity",
                                "responsibility": "responsibility of entity",
                                "schema": {
                                    "etc": "shape of entity",
                                },
                            }
                        ],
                    }
                ],
            )
            return prompt, validate_domains(domains)
        except Exception as error:
            retry += 1
            print(f"retry {retry}")
            print(error)
            if retry > max_retry:
                raise error


def validate_interfaces(interfaces):
    """인터페이스 검증"""
    print(isinstance(interfaces, list))
    print(type(interfaces))
    if not isinstance(interfaces, list):
        raise Exception("interfaces should be array of object")
    for interface in interfaces:
        if not isinstance(interface, dict):
            raise Exception("interface should be object")
        if "name" not in interface:
            raise Exception("interface should have name")
        if "file" not in interface:
            raise Exception("interface should have file")
        if "path" not in interface:
            raise Exception("interface should have path")
        if "code" not in interface:
            raise Exception("interface should have code")
    return interfaces


def validate_interface(interface):
    """인터페이스 검증"""
    print(isinstance(interface, dict))
    print(type(interface))
    if not isinstance(interface, dict):
        raise Exception("interface should be object")
    if "name" not in interface:
        raise Exception("interface should have name")
    if "file" not in interface:
        raise Exception("interface should have file")
    if "path" not in interface:
        raise Exception("interface should have path")
    if "code" not in interface:
        raise Exception("interface should have code")
    return interface


def define_interfaces(domain, service_description):
    """인터페이스 정의"""
    print("try to define interfaces")
    template_prompt = f"""ok, I got your suggestion.
    please give me more detailed data about the interfaces of {domain["name"]}.
    """
    interfaces = []
    for interface in domain["interfaces"]:
        print(interface["name"])
        max_retry = 3
        retry = 0
        while True:
            try:
                prompt, interface = require_json_v2(
                    f"{template_prompt}\nfirstly, I need to know how to implement {interface}",
                    [
                        {
                            "name": "name of interface",
                            "file": "file name of interface",
                            "path": "path of interface. source root is '/'",
                            "code": "code that should be written in the file",
                        }
                    ],
                    service_description,
                )
                interfaces.append(interface)
            except Exception as error:
                retry += 1
                print(domain, error)
                if retry > max_retry:
                    raise Exception("failed to get valid interfaces")
    return template_prompt, validate_interfaces(interfaces)


if __name__ == "__main__":
    context_store = ContextStore()
    prompt, domains = define_domains("simple todo service", "scala", "zio")
    initial_context = context_store.add_context(prompt, domains)
    print(domains)
    # save domains to file
    with open("domains_abs.json", "w") as file:
        file.write(schema_dumps(domains))


    for domain in domains:
        print(domain["name"])
        interfaces = define_interfaces(domain, initial_context.get_context())
        # assign interfaces to domain
        domain["interfaces"] = [*domain["interfaces"], *interfaces]

    # save domains to file
    with open("domains.json", "w") as file:
        file.write(domains)
