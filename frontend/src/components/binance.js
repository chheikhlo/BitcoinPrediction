import React, { useEffect, useState, useRef } from 'react';
import ReactEcharts from 'echarts-for-react';

const Binance = () => {
  const [trades, setTrades] = useState([]); // Pour stocker les trades
  const [predictions, setPredictions] = useState([]); // Pour stocker les prédictions
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@trade');

    ws.current.onmessage = (event) => {
      const tradeData = JSON.parse(event.data);
      console.log('Trade Data:', tradeData);

      // Ajouter le timestamp aux trades pour filtrer plus tard
      const timestamp = Date.now();
      const newTrade = { timestamp, ...tradeData };

      // Mettre à jour les trades, en ne conservant que ceux des dernières 2 heures
      setTrades((prevTrades) => {
        const updatedTrades = [newTrade, ...prevTrades];

        // Filtrer pour ne garder que les trades des dernières 2 heures
        const twoHoursAgo = Date.now() - 2 * 60 * 60 * 1000; // 2 heures en millisecondes
        return updatedTrades.filter(trade => trade.timestamp >= twoHoursAgo);
      });

      // Envoyer les données au backend pour les prédictions
      sendPredictionData(tradeData);
    };

    return () => ws.current.close();
  }, []);

  const sendPredictionData = async (tradeData) => {
    const { p: buyPrice, q: volume } = tradeData; // Extraire le prix d'achat et le volume
    const timestamp = Date.now(); // Obtenir le timestamp actuel

    const dataToSend = {
      data: [[timestamp, buyPrice, buyPrice, volume]] // Préparer les données à envoyer
    };

    try {
      const response = await fetch('http://localhost:5551/api/predictions', {
        method: 'POST', // Utiliser POST pour envoyer des données
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend),
      });

      if (response.ok) {
        const predictionData = await response.json();
        console.log('Prediction Data:', predictionData);
        setPredictions(predictionData); // Mettez à jour les prédictions
      } else {
        console.error('Failed to send data for predictions:', response.statusText);
      }
    } catch (error) {
      console.error('Error sending prediction data:', error);
    }
  };

  // Formater les données pour le graphique ECharts
  const getOption = () => {
    const colors = ['#5470C6', '#EE6666'];

    // Préparer les données avec des timestamps
    const tradeDataWithTime = trades.map(trade => [trade.timestamp, parseFloat(trade.p)]);
    const predictionDataWithTime = predictions.map(prediction => [Date.now(), prediction]); // Adaptez cela en fonction de votre format de données

    return {
      color: colors,
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
        },
      },
      legend: {
        data: ['Real-Time Prices', 'Predicted Prices'],
      },
      grid: {
        top: 70,
        bottom: 50,
      },
      xAxis: {
        type: 'time', // Type time pour l'axe des X
        axisTick: {
          alignWithLabel: true,
        },
      },
      yAxis: {
        type: 'value',
      },
      series: [
        {
          name: 'Real-Time Prices',
          type: 'line',
          data: tradeDataWithTime, // Prix en temps réel avec timestamps
          smooth: true, // Pour une ligne plus fluide
        },
        {
          name: 'Predicted Prices',
          type: 'line',
          data: predictionDataWithTime, // Prédictions avec timestamps
          smooth: true,
        },
      ],
      dataZoom: [
        {
          type: 'slider', // Permettre le zoom via un curseur
          show: true,
          xAxisIndex: [0],
          start: 0, // Pourcentage de la vue initiale
          end: 100,
        },
        {
          type: 'inside', // Zoom à l'aide du défilement de la souris
          xAxisIndex: [0],
          start: 0,
          end: 100,
        },
      ],
    };
  };

  return (
    <div>
      <h2>Bitcoin Prices & Predictions</h2>
      <ReactEcharts option={getOption()} />
    </div>
  );
};

export default Binance;
