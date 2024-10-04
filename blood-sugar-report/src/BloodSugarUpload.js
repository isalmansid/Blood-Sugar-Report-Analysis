// src/BloodSugarUpload.js
import React, { useState } from 'react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import axios from 'axios';

const BloodSugarUpload = () => {
  const [chartOptions, setChartOptions] = useState({
    title: {
      text: 'Blood Sugar Levels Over Time',
    },
    xAxis: {
      categories: [], // Months will go here
      title: {
        text: 'Blood Sugar Readings',
      },
    },
    yAxis: {
      title: {
        text: 'Blood Sugar (mg/dl)',
      },
    },
    series: [
      {
        name: 'Fasting Blood Sugar',
        data: [], // Fasting blood sugar levels will go here
      },
      {
        name: 'Post Lunch Blood Sugar',
        data: [], // Post lunch blood sugar levels will go here
      },
    ],
  });

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    const dataPromises = files.map(file => processFile(file));

    Promise.all(dataPromises).then((results) => {
      const fastingData = [];
      const postLunchData = [];
      const months = results.map((result, index) => `Report ${index + 1}`); // For simplicity

      results.forEach(result => {
        fastingData.push(result.fasting[0] ? parseFloat(result.fasting[0]) : 0); // Get first fasting value
        postLunchData.push(result.postLunch[0] ? parseFloat(result.postLunch[0]) : 0); // Get first post-lunch value
      });

      setChartOptions(prev => ({
        ...prev,
        xAxis: { ...prev.xAxis, categories: months },
        series: [
          { ...prev.series[0], data: fastingData },
          { ...prev.series[1], data: postLunchData },
        ],
      }));
    });
  };

  const processFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  };

  return (
    <div>
      <h1>Upload Blood Sugar PDF Reports</h1>
      <input type="file" multiple onChange={handleFileUpload} />
      <HighchartsReact highcharts={Highcharts} options={chartOptions} />
    </div>
  );
};

export default BloodSugarUpload;
