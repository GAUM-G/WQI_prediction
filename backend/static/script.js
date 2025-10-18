const form = document.getElementById("wqi-form");
const resultDiv = document.getElementById("result");
let currentChart = null;
let currentChartType = 'bar';
let chartData = null;


// WQI categories and colors
function getWqiInfo(wqi) {
    wqi = Number(wqi);
    if (wqi >= 90) return {
        category: "Excellent",
        color: "#4caf50",
        description: "Water quality is exceptional and safe for all uses including drinking.",
        safety: "Very Safe",
        ecosystem: "Minimal Impact",
        health: "No Risk"
    };
    else if (wqi >= 70) return {
        category: "Good",
        color: "#8bc34a",
        description: "Water quality is good and suitable for most purposes with minimal treatment.",
        safety: "Safe",
        ecosystem: "Low Impact",
        health: "Low Risk"
    };
    else if (wqi >= 50) return {
        category: "Moderate",
        color: "#ffeb3b",
        description: "Water quality is acceptable but may require treatment for sensitive uses.",
        safety: "Caution",
        ecosystem: "Moderate Impact",
        health: "Medium Risk"
    };
    else if (wqi >= 25) return {
        category: "Poor",
        color: "#ff9800",
        description: "Water quality is poor and requires significant treatment before use.",
        safety: "Unsafe",
        ecosystem: "High Impact",
        health: "High Risk"
    };
    else return {
        category: "Very Poor",
        color: "#f44336",
        description: "Water quality is very poor and unsuitable for most uses without extensive treatment.",
        safety: "Dangerous",
        ecosystem: "Severe Impact",
        health: "Critical Risk"
    };
}


form.addEventListener("submit", async (e) => {
    e.preventDefault();


    const btn = form.querySelector('.submit-btn');
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Analyzing...</span>';


    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    chartData = data; // Store for chart creation


    try {
        const response = await fetch("/predict", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });


        const result = await response.json();


        if (result.WQI !== undefined) {
            displayResults(result.WQI, data);
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (err) {
        alert("Server Error! Please check if the server is running.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHtml;
    }
});


function displayResults(wqi, data) {
    const info = getWqiInfo(wqi);
    
    // Show results section
    resultDiv.style.display = "block";
    
    // Update WQI display
    document.getElementById('wqi-score').textContent = wqi;
    document.getElementById('wqi-category').textContent = info.category;
    document.getElementById('wqi-category').style.color = info.color;
    document.getElementById('wqi-description').textContent = info.description;
    
    // Update badge color
    const badgeCircle = document.querySelector('.badge-circle');
    badgeCircle.style.background = `linear-gradient(135deg, ${info.color} 0%, ${adjustColor(info.color, -20)} 100%)`;
    
    // Update metrics
    document.getElementById('safety-level').textContent = info.safety;
    document.getElementById('ecosystem-impact').textContent = info.ecosystem;
    document.getElementById('health-risk').textContent = info.health;
    
    // Create initial bar chart
    createChart('bar', data, wqi);
    
    // Scroll to results
    setTimeout(() => {
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
}


// Chart toggle functionality
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        const chartType = this.dataset.chart;
        currentChartType = chartType;
        
        if (chartData) {
            const wqi = document.getElementById('wqi-score').textContent;
            createChart(chartType, chartData, wqi);
        }
    });
});


function createChart(type, data, wqi) {
    const ctx = document.getElementById('waterQualityChart');
    if (!ctx) return;
    
    if (currentChart) {
        currentChart.destroy();
    }
    
    // Calculate averages
    const avgValues = {
        Temperature: (parseFloat(data.Min_Temperature) + parseFloat(data.Max_Temperature)) / 2,
        DO: (parseFloat(data.Min_Dissolved_Oxygen) + parseFloat(data.Max_Dissolved_Oxygen)) / 2,
        pH: (parseFloat(data.Min_pH) + parseFloat(data.Max_pH)) / 2,
        Conductivity: (parseFloat(data.Min_Conductivity) + parseFloat(data.Max_Conductivity)) / 2,
        BOD: (parseFloat(data.Min_BOD) + parseFloat(data.Max_BOD)) / 2,
        Nitrate: (parseFloat(data.Min_Nitrate) + parseFloat(data.Max_Nitrate)) / 2
    };
    
    // ✅ CORRECTED: Ideal limits that match Python WQI calculation (score = 100)
    // These are the thresholds where your Python code gives PERFECT scores
    const idealLimits = {
        Temperature: 25,        // °C - Python gives 90-100 for ≤25°C
        DO: 6.5,                // mg/L - Python gives 100 for 6.5-10 mg/L (start of ideal range)
        pH: 7.0,                // Python gives 100 for 7.0-7.5 (start of ideal range)
        Conductivity: 500,      // µS/cm - Python gives 100 for ≤500 µS/cm
        BOD: 2,                 // mg/L - Python gives 100 for ≤2 mg/L
        Nitrate: 10             // mg/L - Python gives 100 for ≤10 mg/L (best quality)
    };
    
    const labels = ['Temperature (°C)', 'DO (mg/L)', 'pH', 'Conductivity (÷10 µS/cm)', 'BOD (mg/L)', 'Nitrate (mg/L)'];
    const yourData = [
        avgValues.Temperature, 
        avgValues.DO, 
        avgValues.pH, 
        avgValues.Conductivity/10,  // Divided by 10 for visualization
        avgValues.BOD, 
        avgValues.Nitrate
    ];
    const idealData = [
        idealLimits.Temperature, 
        idealLimits.DO, 
        idealLimits.pH, 
        idealLimits.Conductivity/10,  // Divided by 10 to match your data scale
        idealLimits.BOD, 
        idealLimits.Nitrate
    ];
    
    if (type === 'bar') {
        currentChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Your Sample',
                    data: yourData,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 2,
                    borderRadius: 8
                }, {
                    label: 'Ideal Range (Score 100)',
                    data: idealData,
                    backgroundColor: 'rgba(76, 175, 80, 0.8)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `Water Quality Analysis - WQI: ${wqi}`,
                        font: { size: 18, weight: 'bold' },
                        color: '#2d3748',
                        padding: 20
                    },
                    legend: {
                        position: 'top',
                        labels: { font: { size: 13 }, padding: 20 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                
                                // Get the parameter index
                                const paramIndex = context.dataIndex;
                                let value = context.parsed.y;
                                
                                // If it's conductivity (index 3), multiply back by 10 for display
                                if (paramIndex === 3) {
                                    value = Math.round(value * 10);
                                    label += value + ' µS/cm (displayed ÷10)';
                                } else {
                                    const units = ['°C', ' mg/L', '', ' µS/cm', ' mg/L', ' mg/L'];
                                    label += Math.round(value * 10) / 10 + units[paramIndex];
                                }
                                
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 0, 0, 0.05)' },
                        title: {
                            display: true,
                            text: 'Parameter Values (Conductivity shown ÷10)',
                            font: { size: 12, weight: 'bold' },
                            color: '#4a5568'
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    } else {
        // Radar Chart
        currentChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Your Sample',
                    data: yourData,
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(102, 126, 234, 1)',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }, {
                    label: 'Ideal Range (Score 100)',
                    data: idealData,
                    backgroundColor: 'rgba(76, 175, 80, 0.2)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgba(76, 175, 80, 1)',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `Water Quality Radar Analysis - WQI: ${wqi}`,
                        font: { size: 18, weight: 'bold' },
                        color: '#2d3748',
                        padding: 20
                    },
                    legend: {
                        position: 'top',
                        labels: { font: { size: 13 }, padding: 20 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                
                                const paramIndex = context.dataIndex;
                                let value = context.parsed.r;
                                
                                // If it's conductivity (index 3), multiply back by 10
                                if (paramIndex === 3) {
                                    value = Math.round(value * 10);
                                    label += value + ' µS/cm (÷10 for scale)';
                                } else {
                                    const units = ['°C', ' mg/L', '', ' µS/cm', ' mg/L', ' mg/L'];
                                    label += Math.round(value * 10) / 10 + units[paramIndex];
                                }
                                
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 0, 0, 0.1)' },
                        pointLabels: {
                            font: { size: 11, weight: 'bold' },
                            color: '#2d3748'
                        },
                        ticks: {
                            stepSize: 10
                        }
                    }
                }
            }
        });
    }
}


// Helper function to adjust color brightness
function adjustColor(color, amount) {
    return '#' + color.replace(/^#/, '').replace(/../g, color => ('0'+Math.min(255, Math.max(0, parseInt(color, 16) + amount)).toString(16)).substr(-2));
}
