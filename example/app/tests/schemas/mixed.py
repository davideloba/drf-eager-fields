mixed_article_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer"
            },
            "code": {
                "type": "string"
            },
            "description": {
                "type": "string"
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
            "orders": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "created_at": {
                            "type": "date-time"
                        },
                    },
                    "required":["code","description", "created_at"]
                },
            },
            "last_10_orders": {
                "type": "array",
                "minItems": 10,
                "maxItems": 10,
                "items": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "created_at": {
                            "type": "date-time"
                        },
                    },
                    "required":["code","description", "created_at"]
                },
            },
        }
    "required":["code","customer","orders","last_10_orders"]
}