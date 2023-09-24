
### Команди для запуску з GitHub
Без файлів:
```bash
docker run --name lab_2 -p 8080:8080 -t lab_2
```

###  Команди для роботи напряму 
Монтування образу 
```bash
docker build -t lab_2 .
```
Запуск Без файлів:
```bash
docker run --name lab_2 -p 8080:8080 -t lab_2
```

 ###  docker-compose
 Монтування образу:
```bash
docker compose build
```
Запуск контейнеру: 
```bash
docker compose build up
```
