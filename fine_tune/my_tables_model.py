import json
import fine_tune.new_model as new_model
import my_ai


def inject_tables(tables):
    return new_model.create_example("please show all tables", json.dumps(tables))


def get_table_detail(table_name, table_schema):
    return new_model.create_example(
        f"please show detail of {table_name}", f"{table_schema}"
    )


def get_all_tables():
    return [
        {
            "name": "courses",
            "schema": [
                {"name": "id", "type": "int"},
                {"name": "name", "type": "string"},
            ],
        },
        {
            "name": "users",
            "schema": [
                {"name": "id", "type": "int"},
                {"name": "name", "type": "string"},
            ],
        },
        {
            "name": "enrollments",
            "schema": [
                {"name": "id", "type": "int"},
                {"name": "user_id", "type": "int"},
                {"name": "course_id", "type": "int"},
            ],
        },
        {
            "name": "grades",
            "schema": [
                {"name": "id", "type": "int"},
                {"name": "user_id", "type": "int"},
                {"name": "course_id", "type": "int"},
                {"name": "grade", "type": "int"},
            ],
        },
        {
            "name": "teachers",
            "schema": [
                {"name": "id", "type": "int"},
                {"name": "user_id", "type": "int"},
                {"name": "course_id", "type": "int"},
            ],
        },
        {
            "name": "orders",
            "schema": [
                {"name": "id", "type": "int"},
                {"name": "user_id", "type": "int"},
                {"name": "product_id", "type": "int"},
                {"name": "quantity", "type": "int"},
            ],
        },
        {
            "name": "products",
            "schema": [
                {"name": "id", "type": "int"},
                {"name": "name", "type": "string"},
                {"name": "price", "type": "int"},
            ],
        },
        {
            "name": "materials",
            "schema": [
                {"name": "id", "type": "int"},
                {"name": "name", "type": "string"},
                {"name": "price", "type": "int"},
            ],
        },
        {
            "name": "homeworks",
            "schema": [
                {"name": "id", "type": "int"},
                {"name": "user_id", "type": "int"},
                {"name": "course_id", "type": "int"},
                {"name": "grade", "type": "int"},
            ],
        },
        {
            "name": "exams",
            "schema": [
                {"name": "id", "type": "int"},
                {"name": "user_id", "type": "int"},
                {"name": "course_id", "type": "int"},
                {"name": "grade", "type": "int"},
            ],
        },
    ]


def init_model(tables):
    table_names = [table["name"] for table in tables]
    examples = [inject_tables(table_names)]

    for table in tables:
        examples.append(get_table_detail(table["name"], table["schema"]))

    return new_model.create_conversation(examples)


def main():
    tables = get_all_tables()
    context = init_model(tables)
    prompt = """redshift Query to get the name of a course and the average grade for that course from students who have taken the course without paying and only those with a grade of C or lower, and never taken course named 'meth basic'."""
    prompt, result = my_ai.require_json_v2(prompt, [
        {
            "field_name": "query",
            "field_description": "query",
            "value_type": "string",
        }
    ], context)


if __name__ == "__main__":
    main()
