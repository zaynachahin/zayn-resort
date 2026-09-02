-- Creates sample data for local development
-- Execute after schema.sql


INSERT INTO customers(id, full_name, date_of_birth, cpf, newsletter_opt_in, created_at)
VALUES
('d3fac323-9b89-4ec8-b05d-b1ef54e0b0eb', 'Zayn Chahin', '1999-03-01', '21481912370', false, '2026-05-17 19:27:28.457555'),
('e7cd8f4f-9cf3-4be8-a700-24575018f0dd', 'Mario Silva', '1989-11-28', '39506754807', true, '2026-05-05 12:19:29'),
('ce53b13c-0937-4b67-a9f7-f32fde8737a8', 'Luis Henrique', '1976-07-09', '21389202478', false, '2026-05-17 19:27:28.457555'),
('be383bb5-7615-42bc-9e64-eeecbf5d475a', 'Maria Barbosa', '1900-02-01', '84729350493', true, '2026-05-17 18:30:00');


INSERT INTO room_category(id, name, capacity, daily_rate, created_at)
VALUES
('81c8dc30-955e-4fb0-b338-7ac6dcb87c83', 'Comum', 2, 2000.00, '2026-05-17 19:46:48.869761'),
('e2dc0235-562a-4aa4-9022-a5b7086ad4fa', 'Premium', 4, 4000.00, '2026-05-17 19:46:48.869761');


INSERT INTO rooms(id, name, room_category_id, description, created_at)
VALUES
('f19c172c-a43d-4a4c-b657-146d5ec28c25', 'Ocean View', 'e2dc0235-562a-4aa4-9022-a5b7086ad4fa', 'Suíte premium com varanda privativa, vista panorâmica para o mar e cama king size.', NOW()),
('42f972af-2749-48c7-8c6f-8437bfac6873', 'Blue Lagoon', 'e2dc0235-562a-4aa4-9022-a5b7086ad4fa', 'Quarto moderno com decoração tropical, iluminação natural e ambiente relaxante.', NOW()),
('372bc3e7-45c3-4a68-b869-abb79bc5e9a4', 'Crystal Bay Room', 'e2dc0235-562a-4aa4-9022-a5b7086ad4fa', 'Suíte moderna equipada com varanda, ar-condicionado e iluminação aconchegante.', NOW()),
('d913ad20-668e-4ca9-8291-5518289dabf1', 'Bamboo Deluxe', 'e2dc0235-562a-4aa4-9022-a5b7086ad4fa', 'Quarto elegante com móveis sofisticados, decoração natural e clima acolhedor.', NOW()),
('1c9d8f32-3483-4bd9-aa55-897d3aea8eb1', 'Paradise Garden', 'e2dc0235-562a-4aa4-9022-a5b7086ad4fa', 'Quarto espaçoso com vista para o jardim tropical e ambiente silencioso.', NOW()),
('697a7aa1-09d4-47d7-96c7-33048d34b5c0', 'Blue Coast', '81c8dc30-955e-4fb0-b338-7ac6dcb87c83', 'Ambiente confortável com decoração tropical e ótima experiência de hospedagem.', NOW());


INSERT INTO reservations(customer_id, room_id, check_in, check_out, status, total_amount, created_at)
VALUES
('d3fac323-9b89-4ec8-b05d-b1ef54e0b0eb', 'f19c172c-a43d-4a4c-b657-146d5ec28c25', '2026-09-01', '2026-09-06', 'confirmed', 20000.00, '2026-08-01 10:00:00'),
('d3fac323-9b89-4ec8-b05d-b1ef54e0b0eb', '42f972af-2749-48c7-8c6f-8437bfac6873', '2026-07-10', '2026-07-13', 'checked_out', 12000.00, '2026-06-15 09:00:00'),
('d3fac323-9b89-4ec8-b05d-b1ef54e0b0eb', '372bc3e7-45c3-4a68-b869-abb79bc5e9a4', '2026-08-01', '2026-08-03', 'cancelled', 8000.00, '2026-07-01 14:00:00'),
('e7cd8f4f-9cf3-4be8-a700-24575018f0dd', 'f19c172c-a43d-4a4c-b657-146d5ec28c25', '2026-08-18', '2026-08-22', 'checked_in', 16000.00, '2026-08-10 11:00:00'),
('ce53b13c-0937-4b67-a9f7-f32fde8737a8', 'd913ad20-668e-4ca9-8291-5518289dabf1', '2026-09-10', '2026-09-12', 'confirmed', 8000.00, '2026-08-05 15:00:00'),
('ce53b13c-0937-4b67-a9f7-f32fde8737a8', '697a7aa1-09d4-47d7-96c7-33048d34b5c0', '2026-06-20', '2026-06-25', 'checked_out', 10000.00, '2026-06-01 10:00:00'),
('be383bb5-7615-42bc-9e64-eeecbf5d475a', '1c9d8f32-3483-4bd9-aa55-897d3aea8eb1', '2026-10-01', '2026-10-08', 'confirmed', 28000.00, '2026-08-20 09:00:00'),
('be383bb5-7615-42bc-9e64-eeecbf5d475a', '697a7aa1-09d4-47d7-96c7-33048d34b5c0', '2026-07-15', '2026-07-18', 'checked_out', 6000.00, '2026-07-01 18:00:00');