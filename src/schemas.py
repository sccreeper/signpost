create_url_schema = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "description": "",
  "type": "object",
  "properties": {
    "slug": {
      "type": "string"
    },
    "url": {
      "type": "string"
    }
  },
  "required": [
    "slug",
    "url"
  ]
}

delete_url_schema = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "description": "",
  "type": "object",
  "properties": {
    "id": {
      "type": "string"
    },
    "slug": {
      "type": "string"
    }
  },
  "required": [
    "id",
    "slug"
  ]
}

modify_url_schema = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "description": "",
  "type": "object",
  "properties": {
    "id": {
      "type": "string"
    },
    "new_values": {
      "type": "object",
      "properties": {
        "slug": {
          "type": "string"
        },
        "url": {
          "type": "string"
        },
        "enabled": {
          "type": "boolean"
        },
        "opaque": {
          "type": "boolean"
        },
        "password": {
          "type": "string"
        }
      },
      "required": [
        "slug",
        "url",
        "enabled",
        "opaque",
        "password"
      ]
    }
  },
  "required": [
    "id",
    "new_values"
  ]
}

