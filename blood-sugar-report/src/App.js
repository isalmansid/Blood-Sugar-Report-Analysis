import React, { useState } from 'react';
import axios from 'axios';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import './App.css';

const App = () => {
    const [files, setFiles] = useState(null);
    const [data, setData] = useState([]);
    const [error, setError] = useState('');

    const processFile = async () => {
        if (!files) return;

        const formData = new FormData();
        Array.from(files).forEach((file) => {
            formData.append('files', file);
        });

        try {
            const response = await axios.post('http://localhost:5000/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setData(prevData => [...prevData, ...response.data]); // Merge new data with existing data
            setError(''); // Clear any previous errors
        } catch (error) {
            console.error('Error uploading files:', error);
            setError('Error uploading files. Please try again.');
        }
    };

    const getChartOptions = () => {
        const monthDataMap = new Map(); // Map to aggregate data by month

        // Aggregate data for charting
        data.forEach(item => {
            const month = item.month;
            const fastingReading = item.fasting.length > 0 ? parseFloat(item.fasting[0]) : null;
            const postLunchReading = item.post_lunch.length > 0 ? parseFloat(item.post_lunch[0]) : null;

            // Initialize if month not in the map
            if (!monthDataMap.has(month)) {
                monthDataMap.set(month, { fasting: [], postLunch: [] });
            }

            // Push readings to the respective arrays
            if (fastingReading !== null) monthDataMap.get(month).fasting.push(fastingReading);
            if (postLunchReading !== null) monthDataMap.get(month).postLunch.push(postLunchReading);
        });

        // Prepare final data arrays for Highcharts
        const months = [...monthDataMap.keys()];
        const fastingLevels = months.map(month => {
            const values = monthDataMap.get(month).fasting;
            return values.length > 0 ? values[0] : null;
        });
        const postLunchLevels = months.map(month => {
            const values = monthDataMap.get(month).postLunch;
            return values.length > 0 ? values[0] : null;
        });

        return {
            chart: {
                type: 'line',
                height: '400px', // a fixed height for the chart
            },
            title: {
                text: 'Blood Sugar Levels Comparison',
            },
            xAxis: {
                categories: months,
                title: {
                    text: 'Months',
                },
                gridLineWidth: 0,
            },
            yAxis: {
                title: {
                    text: 'Blood Sugar Level (mg/dl)',
                },
                gridLineWidth: 0,
            },
            series: [
                {
                    name: 'Fasting Blood Sugar',
                    data: fastingLevels,
                    type: 'line',
                },
                {
                    name: 'Post Lunch Blood Sugar',
                    data: postLunchLevels,
                    type: 'line',
                },
            ],
            plotOptions: {
                series: {
                    dataLabels: {
                        enabled: true,
                    },
                },
            },
        };
    };

    return (
        <div className="container">
            <h1>Blood Sugar Report Analysis</h1>
            <input
                type="file"
                multiple
                onChange={(e) => setFiles(e.target.files)}
            />
            <button onClick={processFile}>Upload</button>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {/*{data.length > 0 && <div className="chart-title">Blood Sugar Levels Comparison</div>}*/}
            <div className="highcharts-container">
                {data.length > 0 && (
                    <HighchartsReact
                        highcharts={Highcharts}
                        options={getChartOptions()}
                    />
                )}
            </div>
        </div>
    );
};


export default App;
