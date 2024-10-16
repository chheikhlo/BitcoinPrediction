import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';

const BitcoinPrediction = () => {
  const [trades, setTrades] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@trade');

    ws.current.onopen = () => console.log("WebSocket connecté");

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const formattedTrade = {
        timestamp: data.T,  // Timestamp de la transaction
        price: parseFloat(data.p),  // Prix de la transaction
        volume: parseFloat(data.q)  // Volume échangé
      };

      setTrades((prevTrades) => [formattedTrade, ...prevTrades].slice(0, 100));

      // Envoyer les données au backend Flask
      axios.post('http://localhost:5551/api/send_trade_data', formattedTrade)
        .catch(error => console.error("Erreur Axios :", error));
    };

    return () => ws.current.close();
  }, []);

  // Récupérer les prédictions depuis le backend Flask
  useEffect(() => {
    if (trades.length > 0) {
      const latestVolume = trades[0].volume;  // Utiliser le volume du dernier trade reçu

      axios.post('http://localhost:5551/api/get_predictions', { volume: latestVolume })  // Envoyer le volume au backend
        .then(response => setPredictions(prevPredictions => [...prevPredictions, response.data.prediction]))
        .catch(error => console.error("Erreur Axios :", error));
    }
  }, [trades]);

  // Configuration du graphique avec ECharts
  const option = {
    title: {
      text: 'BTC/USDT Cours et prédictions'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: trades.map(trade => new Date(trade.timestamp).toLocaleTimeString())  // Affiche le timestamp sur l'axe des X
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: 'Prix de transaction',
        type: 'line',
        data: trades.map(trade => trade.price)
      },
      {
        name: 'Prédictions',
        type: 'line',
        data: predictions
      }
    ]
  };

  return (
    <div>
      <h2>Graphique en temps réel : BTC/USDT avec prédictions</h2>
      <ReactECharts option={option} />
    </div>
  );
};

export default BitcoinPrediction;
