--- Table urgency
CREATE TABLE public.urgency (
	id INT GENERATED ALWAYS AS IDENTITY NOT NULL,
	"name" VARCHAR(15) NOT NULL,
	create_date DATE DEFAULT CURRENT_DATE,
	CONSTRAINT urgency_pk PRIMARY KEY (id),
	CONSTRAINT urgency_unique UNIQUE ("name")
);
COMMENT ON TABLE public.urgency IS 'Уровень важности уведомления.';

-- urgency`s column comments
COMMENT ON COLUMN public.urgency.id IS 'ID уровня уведомления.';
COMMENT ON COLUMN public.urgency."name" IS 'Название уровня уведомления.';


--- Table repeat
CREATE TABLE public.repeat (
	id INT GENERATED ALWAYS AS IDENTITY NOT NULL,
	"name" VARCHAR(15) NOT NULL,
	description VARCHAR(15) NOT NULL,
	"count" INT CHECK ("count" > 0) CHECK("count" < 365),
	create_date DATE DEFAULT CURRENT_DATE,
	CONSTRAINT repeat_pk PRIMARY KEY (id),
	CONSTRAINT repeat_unique_name UNIQUE ("name"),
	CONSTRAINT repeat_unique_count UNIQUE ("count")
);
COMMENT ON TABLE public.repeat IS 'Таблица с периодами повторений.';

-- repeat`s column comments
COMMENT ON COLUMN public.repeat.id IS 'ID периодов повторений уведомлений.';
COMMENT ON COLUMN public.repeat."name" IS 'Название периодов повторений.';
COMMENT ON COLUMN public.repeat."count" IS 'Период повторений.';
COMMENT ON COLUMN public.repeat.description IS 'Подробное описание повторений.';


--- Table reminder
CREATE TABLE public.reminder (
	"uuid" UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
	create_data DATE DEFAULT CURRENT_DATE,
    target_data DATE NOT NULL,
    target_time TIME NOT NULL,
	status boolean DEFAULT FALSE NOT NULL,
	mongo_uuid VARCHAR(24) NOT NULL UNIQUE,
	urgency_id INT NOT NULL,
	repeat_id INT DEFAULT NULL,
	CONSTRAINT reminder_urgency_fk FOREIGN KEY (urgency_id) REFERENCES public.urgency(id),
	CONSTRAINT reminder_repeat_fk FOREIGN KEY (repeat_id) REFERENCES public.repeat(id)
);
COMMENT ON TABLE public.reminder IS 'Напоминания пользователя.';

-- reminder`s column comments
COMMENT ON COLUMN public.reminder."uuid" IS 'ID уведомления.';
COMMENT ON COLUMN public.reminder.create_data IS 'Дата создания уведомления.';
COMMENT ON COLUMN public.reminder.target_data IS 'Дата исполнения уведомления.';
COMMENT ON COLUMN public.reminder.target_time IS 'Время исполнения уведомления.';
COMMENT ON COLUMN public.reminder.status IS 'Статус выполнения.';
COMMENT ON COLUMN public.reminder.mongo_uuid IS 'Ссылка на тело уведомления.';
COMMENT ON COLUMN public.reminder.urgency_id IS 'ID уровня важности уведомления.';
COMMENT ON COLUMN public.reminder.repeat_id IS 'ID повторения уведомления.';