db.createCollection("Notifications", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Валидатор уведомлений пользователя",
            required: ["title", "action"],
            properties: {
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
    action: ["show"],
    title: "Linux Accompaniment",
    description: "Приложение LA запущено!"
});
