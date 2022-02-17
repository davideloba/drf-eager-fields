eager_loading_schema = {
    "type": "object",
    "properties": {
        "code": {
            "type": "string"
        },
        "last_10_orders": {
            "type": "array",
            "minItems": 10,
            "maxItems": 10,
            "items": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string"
                    },
                    "customer": {
                        "type": "object",
                        "properties": {
                            "description"{
                                "type": "string"
                            },
                        },
                    },
                },
                "required":["description","customer"]
            },
        },
        "customer": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "name": {
                    "type": "integer"
                },
                "countries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            },
                            "region": {
                                "type": "object",
                                "properties": {
                                    "name"{
                                        "type": "string"
                                    },
                                }
                            }
                        }
                    }
                },
            },
            "required":["id","name", "countries"]
        },
    "required":["code","last_10_orders", "customer"]
}