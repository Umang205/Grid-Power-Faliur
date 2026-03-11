// DOM Content Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initLoadChart();
    initHeatmap();
    initRiskGauge();
    setupEventListeners();
    
    // Show loading animation
    simulateDataLoading();
});

// 1. Real-Time Load Fluctuation Chart
function initLoadChart() {
    const ctx = document.getElementById('loadChart').getContext('2d');
    
    // Sample data for the chart
    const labels = Array.from({length: 24}, (_, i) => `${i}:00`);
    const data = Array.from({length: 24}, () => Math.floor(Math.random() * 100));
    
    window.loadChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Load Percentage',
                data: data,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#2d3748',
                        font: {
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 58, 138, 0.9)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#1e3a8a',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(226, 232, 240, 0.5)'
                    },
                    ticks: {
                        color: '#64748b'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#64748b'
                    }
                }
            }
        }
    });

    // Simulate real-time updates
    setInterval(() => {
        const newData = loadChart.data.datasets[0].data.map(value => {
            const change = Math.random() * 10 - 5;
            return Math.min(100, Math.max(0, value + change));
        });
        
        loadChart.data.datasets[0].data = newData;
        loadChart.update();
    }, 3000);
}

// 2. Regional Grid Stress Heatmap
function initHeatmap() {
    const container = document.getElementById('heatmap');
    const width = container.clientWidth;
    const height = 300;
    
    // Sample regions data
    const regions = [
        { name: "North", value: Math.random() * 100 },
        { name: "South", value: Math.random() * 100 },
        { name: "East", value: Math.random() * 100 },
        { name: "West", value: Math.random() * 100 },
        { name: "Central", value: Math.random() * 100 }
    ];
    
    // Create SVG container
    const svg = d3.select('#heatmap')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Create heatmap cells
    const cellSize = Math.min(width / regions.length, 80);
    const xPadding = (width - (cellSize * regions.length)) / 2;
    
    svg.selectAll('.heatmap-cell')
        .data(regions)
        .enter()
        .append('rect')
        .attr('class', 'heatmap-cell')
        .attr('x', (d, i) => xPadding + i * cellSize)
        .attr('y', height / 2 - cellSize / 2)
        .attr('width', cellSize - 10)
        .attr('height', cellSize - 10)
        .attr('rx', 8)
        .attr('fill', d => getStressColor(d.value))
        .on('mouseover', function(event, d) {
            showTooltip(event, `${d.name}: ${d.value.toFixed(1)}% stress`);
            d3.select(this).attr('stroke', '#1d4ed8').attr('stroke-width', 2);
        })
        .on('mouseout', function() {
            hideTooltip();
            d3.select(this).attr('stroke', 'white').attr('stroke-width', 1);
        });
    
    // Add region labels
    svg.selectAll('.region-label')
        .data(regions)
        .enter()
        .append('text')
        .attr('class', 'region-label')
        .attr('x', (d, i) => xPadding + i * cellSize + cellSize / 2 - 5)
        .attr('y', height / 2 + cellSize / 2 + 20)
        .attr('text-anchor', 'middle')
        .attr('fill', '#2d3748')
        .text(d => d.name);
    
    // Tooltip functions
    function showTooltip(event, content) {
        const tooltip = d3.select('body').append('div')
            .attr('class', 'tooltip')
            .style('position', 'absolute')
            .style('background', 'rgba(30, 58, 138, 0.9)')
            .style('color', 'white')
            .style('padding', '8px 16px')
            .style('border-radius', '4px')
            .style('pointer-events', 'none')
            .html(content);
        
        tooltip.style('left', (event.pageX + 10) + 'px')
               .style('top', (event.pageY - 30) + 'px');
    }
    
    function hideTooltip() {
        d3.select('.tooltip').remove();
    }
    
    function getStressColor(value) {
        if (value < 30) return '#4CAF50';  // Green (low stress)
        if (value < 70) return '#FFC107';  // Yellow (medium stress)
        return '#FF3E41';                  // Red (high stress)
    }
}

// 3. Risk Gauge Visualization
function initRiskGauge() {
    const container = document.getElementById('riskGauge');
    const width = container.clientWidth;
    const height = 200;
    
    // Sample risk level (0-100)
    const riskLevel = Math.random() * 100;
    
    // Create SVG container
    const svg = d3.select('#riskGauge')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Create gauge background
    const gaugeWidth = width * 0.8;
    const gaugeHeight = 20;
    const gaugeX = (width - gaugeWidth) / 2;
    const gaugeY = height / 2 - gaugeHeight / 2;
    
    // Gradient for risk level
    const gradient = svg.append('defs')
        .append('linearGradient')
        .attr('id', 'risk-gradient')
        .attr('x1', '0%')
        .attr('y1', '0%')
        .attr('x2', '100%')
        .attr('y2', '0%');
    
    gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', '#4CAF50');
    
    gradient.append('stop')
        .attr('offset', '50%')
        .attr('stop-color', '#FFC107');
    
    gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', '#FF3E41');
    
    // Draw gauge background
    svg.append('rect')
        .attr('x', gaugeX)
        .attr('y', gaugeY)
        .attr('width', gaugeWidth)
        .attr('height', gaugeHeight)
        .attr('rx', gaugeHeight / 2)
        .attr('fill', 'url(#risk-gradient)');
    
    // Draw risk indicator
    const indicator = svg.append('circle')
        .attr('cx', gaugeX + (gaugeWidth * riskLevel / 100))
        .attr('cy', gaugeY + gaugeHeight / 2)
        .attr('r', 12)
        .attr('fill', getRiskColor(riskLevel))
        .attr('stroke', 'white')
        .attr('stroke-width', 2);
    
    // Add risk level text
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', gaugeY + gaugeHeight + 30)
        .attr('text-anchor', 'middle')
        .attr('fill', getRiskColor(riskLevel))
        .attr('font-weight', 'bold')
        .attr('font-size', '24px')
        .text(`${riskLevel.toFixed(1)}%`);
    
    // Add risk label
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', gaugeY + gaugeHeight + 50)
        .attr('text-anchor', 'middle')
        .attr('fill', '#64748b')
        .text(getRiskLabel(riskLevel));
    
    function getRiskColor(value) {
        if (value < 30) return '#4CAF50';  // Green (low risk)
        if (value < 70) return '#FFC107';  // Yellow (medium risk)
        return '#FF3E41';                  // Red (high risk)
    }
    
    function getRiskLabel(value) {
        if (value < 30) return 'Low Risk';
        if (value < 70) return 'Medium Risk';
        return 'High Risk - Immediate Attention Needed';
    }
}

// 4. Event Listeners and Form Handling
function setupEventListeners() {
    // Form submission handler
    const analysisForm = document.querySelector('form');
    analysisForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const region = this.querySelector('select').value;
        const loadLevel = parseFloat(this.querySelector('input').value);
        
        if (isNaN(loadLevel) || loadLevel < 0 || loadLevel > 100) {
            showAlert('Please enter a valid load percentage (0-100)', 'error');
            return;
        }
        
        // Simulate analysis
        showAlert(`Analysis started for ${region} region with ${loadLevel}% load`, 'success');
        
        // Update charts with new data
        setTimeout(() => {
            updateChartsWithNewData(region, loadLevel);
            showAlert(`Analysis complete for ${region} region`, 'success');
        }, 2000);
    });
    
    // Alert function
    function showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
            type === 'error' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
        }`;
        alert.textContent = message;
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.classList.add('opacity-0', 'transition-opacity', 'duration-500');
            setTimeout(() => alert.remove(), 500);
        }, 3000);
    }
}

// 5. Data Simulation and Updates
function simulateDataLoading() {
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'fixed inset-0 flex items-center justify-center bg-white bg-opacity-90 z-50';
    loadingIndicator.innerHTML = `
        <div class="text-center">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#3b82f6]"></div>
            <p class="mt-4 text-[#1e3a8a] font-semibold">Loading grid data...</p>
        </div>
    `;
    document.body.appendChild(loadingIndicator);
    
    setTimeout(() => {
        loadingIndicator.classList.add('opacity-0', 'transition-opacity', 'duration-500');
        setTimeout(() => loadingIndicator.remove(), 500);
    }, 1500);
}

function updateChartsWithNewData(region, loadLevel) {
    // Update load chart with new data point
    if (window.loadChart) {
        const now = new Date();
        const timeLabel = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
        
        // Add new data point and remove oldest if needed
        const chart = window.loadChart;
        chart.data.labels.push(timeLabel);
        chart.data.datasets[0].data.push(loadLevel);
        
        if (chart.data.labels.length > 24) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        
        chart.update();
    }
    
    // Update heatmap with new region data
    d3.select('#heatmap svg').remove();
    initHeatmap();
    
    // Update risk gauge
    d3.select('#riskGauge svg').remove();
    initRiskGauge();
}