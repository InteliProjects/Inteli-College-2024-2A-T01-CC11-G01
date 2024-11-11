import React, { useEffect, useState } from "react";
import logo from "./logo.svg";
import "./App.css";

function App() {

  const [messages, setMessages] = useState<{ sender: string, content: string }[]>([]);

  useEffect(() => {

    

    console.log("conectando ao servidor de eventos");
    const sse = new EventSource("http://localhost:3001/events", {
      withCredentials: true,
    });

    function getRealtimeData(data: any) {
      console.log(data)
    }

    sse.onmessage = (e) => {
      getRealtimeData(e.data);
    };

    sse.onerror = (e: any) => {
      console.log("erro ao conectar ao servidor de eventos");
      console.log(e);
      sse.close();
    };

    return () => {
      sse.close();
    };
  }, []);

  function sendMessage() {
    fetch("http://localhost:3001/send-message", {
      method: "POST",
      body: JSON.stringify({ message: "Hello, World!" }),
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  return (
    <div className="container">
      <div className="chat-container">
        <ul>

        </ul>
        <button onClick={sendMessage}>Send Message</button>
      </div>
    </div>
  );
}

export default App;
