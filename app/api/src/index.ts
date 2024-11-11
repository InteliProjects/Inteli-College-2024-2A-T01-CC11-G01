import express, { Request, Response } from 'express';
import mongoose from 'mongoose';
import amqp from 'amqplib';
import cors from 'cors';

const app = express();

app.use(cors());

const PORT = 3002;

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://db:27017/chat';
const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://messaging:5672';
let channel: amqp.Channel;

interface IMessage extends mongoose.Document {
  username: string;
  message: string;
  timestamp: Date;
}

const messageSchema = new mongoose.Schema({
  username: { type: String, required: true },
  message: { type: String, required: true },
  timestamp: { type: Date, default: Date.now }
});

const Message = mongoose.model<IMessage>('Message', messageSchema);

// Middleware
app.use(express.json());

async function connectMongoDB() {
  const maxRetries = 5;
  let retries = 0;

  while (retries < maxRetries) {
    try {
      await mongoose.connect(MONGODB_URI);
      console.log('Conectado ao MongoDB');
      return;
    } catch (error) {
      retries++;
      console.log(`Tentativa de conexão ao MongoDB ${retries}/${maxRetries} falhou. Tentando novamente em 5 segundos...`);
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  }

  throw new Error('Não foi possível conectar ao MongoDB após várias tentativas.');
}

// Função de conexão ao RabbitMQ com lógica de retry e timeout
async function setupRabbitMQ() {
  const maxRetries = 10;
  let retries = 0;

  while (retries < maxRetries) {
    try {
      const connection = await amqp.connect(RABBITMQ_URL);
      channel = await connection.createChannel();
      await channel.assertQueue('messages', { durable: false });
      console.log('Conectado ao RabbitMQ');
      return;
    } catch (error) {
      retries++;
      console.log(`Tentativa de conexão ao RabbitMQ ${retries}/${maxRetries} falhou. Tentando novamente em 5 segundos...`);
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  }

  throw new Error('Não foi possível conectar ao RabbitMQ após várias tentativas.');
}

// Endpoints
app.post('/messages', async (req: Request, res: Response) => {
  const { username, message } = req.body;
  const newMessage = new Message({ username, message });
  await newMessage.save();

  // Publica a mensagem no RabbitMQ
  channel.sendToQueue('messages', Buffer.from(JSON.stringify({
    username: newMessage.username,
    message: newMessage.message,
    timestamp: newMessage.timestamp
  })));

  res.status(201).json(newMessage);
});

app.get('/messages', async (req: Request, res: Response) => {
  const messages = await Message.find().sort({ timestamp: 1 });
  res.json(messages);
});

// Inicia o servidor após configurar RabbitMQ e MongoDB
app.listen(PORT, async () => {
  console.log(`API rodando na porta ${PORT}`);

  // Tenta conectar ao MongoDB e RabbitMQ com lógica de retry
  await connectMongoDB();
  await setupRabbitMQ();
});
