db.createCollection("Notifications", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Валидатор уведомлений пользователя",
            required: ["name", "title", "action"],
            properties: {
                name: {
                    bsonType: "string",
                    description: "Название сообщения должно быть `string`!"
                },
                title: {
                    bsonType: "string",
                    description: "Заголовок сообщения должен быть `string`!"
                },
                description: {
                    bsonType: "string",
                    description: "Полное описание сообщение должно быть `string`!"
                },
                action: {
                    bsonType: "array",
                    description: "Действие уведомления должно быть уникальным `list[str]`!",
                    minItems: 1,
                    uniqueItems: true,
                    items: {
                        bsonType: "string",
                        description: "Действие уведомления должно быть `str`!"
                    }
                }
            }
        }
    }
});

db.Notifications.insertOne({
    _id: ObjectId('670532d3acf02dec8d964037'),
    name: "default message",
    action: ["show"],
    title: "Linux Accompaniment",
    description: "Приложение LA запущено!"
});
