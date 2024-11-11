import express, { Request, Response } from "express";
import http from "http";
import cors from "cors";
import { connect, Channel, Connection } from "amqplib";

const app = express();
const server = http.createServer(app);

app.use(
  cors({
    credentials: true,
    origin: true,
  })
);
app.use(express.json());

const RABBITMQ_URL = "amqp://messaging:5672";
let channel: Channel;
const PORT = 3001;
let value = 0;

let clients: Response[] = [];

async function setupRabbitMQ() {
  try {
    const connection: Connection = await connect(RABBITMQ_URL);
    channel = await connection.createChannel();
    await channel.assertQueue("messages", { durable: false });

    channel.consume("messages", (msg) => {
      if (msg) {
        const message = msg.content.toString();
        clients.forEach((res) => res.write(`data: ${message}\n\n`));
        channel.ack(msg);
      }
    });

    console.log("Conectado ao RabbitMQ e consumindo mensagens");
  } catch (error) {
    console.error("Erro ao conectar ao RabbitMQ:", error);
    setTimeout(setupRabbitMQ, 5000);
  }
}
app.get("/events", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:3000");
  res.setHeader("Access-Control-Allow-Credentials", "true");

  console.log("New client connected");

  clients.push(res);

  req.on("close", () => {
    console.log("Client disconnected");
    clients = clients.filter((client) => client !== res);
  });
});

app.get("/health", (req, res) => {
  res.status(200).json({ status: "ok" });
});

app.get("/messages", (req, res) => {
  res.status(200).json({ messages: ["Hello, World!"] });
});

app.post("/send-message", async (req: Request, res: Response) => {
  if (!req.body) {
    return res
      .status(400)
      .json({ error: "Corpo da requisição não pode ser vazio" });
  }

  const { message } = req.body;

  if (!message) {
    return res.status(400).json({ error: "A mensagem é obrigatória" });
  }

  try {
    await channel.sendToQueue("messages", Buffer.from(message));
    res.status(200).json({ success: "Mensagem enviada com sucesso" });
  } catch (error) {
    res
      .status(500)
      .json({ error: "Erro ao enviar a mensagem para o RabbitMQ" + error });
  }
});

server.listen(3001, () => {
  console.log("server started at port 3001");
  setupRabbitMQ();
});
