"""백엔드 코파일럿"""
from my_ai import require_json

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


def define_domains(service_description):
    """도메인 정의"""
    print("try to define domains")
    template_prompt = f"""I'm trying to make a service like this
"{service_description}"

Divide this service by domain.
And make each domain into array of object json according to the format below
[{{name: name of domain,
responsibility: what responsibilities the domain has,
interfaces: [{{name: name of interface,
    responsibility: responsibility of interface}}, ...](it should be about what actions the domain can do)
entities: [
    {{name: name of entity,
    responsibility: responsibility of entity,
    schema: json object that show shape of entity}}, ...]}}, ...]
"""
    
    max_retry = 3
    retry = 0
    while True:
        try:
            domains = require_json(template_prompt)
            validated_domains = validate_domains(domains)
            break
        except Exception as error:
            retry += 1
            print(f"retry {domains}")
            print(error)
            if retry > max_retry:
                raise Exception("failed to get valid domains")

    return validated_domains


if __name__ == "__main__":
    SERVICE = """simple todo application"""
    domains = define_domains(SERVICE)
    print(domains)
