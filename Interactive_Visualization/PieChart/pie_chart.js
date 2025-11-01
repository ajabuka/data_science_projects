// Format number with commas and 2 decimal places
function formatNumber(num) {
    return num.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// Main visualization function
function initializeVisualization() {
    // Set up chart dimensions
    const width = 1000;
    const height = 550;
    const radius = Math.min(width, height) / 2 - 40;
    const labelRadius = radius * 1.2; // Radius for label positioning
    
    // Create SVG
    const svg = d3.select(".pie_chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    // Main chart group
    const chartGroup = svg.append("g")
        .attr("transform", `translate(${width/2},${height/2})`);
    
    // Color scale
    const color = {
        FraudFlag: {
            "TRUE": "orange",
            "FALSE": "green",
        },
        TransactionStatus: {
            "Success": "#800080",
            "Failed": "#A52A2A",
        },
        DeviceUsed: {
            "Mobile": "#008080",
            "Desktop": "#000080",
        },
        TransactionType: {
            "Cheque Deposit": "#0000FF",
            "Deposit": "#800000",
            "Withdrawal": "#FFC0CB",
            "Transfer": "#87CEEB",
            "ATM Withdrawal": "#808000",
            "Online Transfer": "#FFFF00",
            "Bill Payment": "#00FFFF",
            "POS Withdrawal": "#C8A2C8"
        }
    };
    
    // Pie layout
    const pie = d3.pie()
        .value(d => d.value)
        .sort(null);
    
    // Arc generator
    const arc = d3.arc()
        .innerRadius(0)
        .outerRadius(radius);
    
    // Tooltip
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip");
    
    // Breadcrumb for navigation
    const breadcrumb = d3.select("#breadcrumb");
    
    // Load and process data
    d3.csv("new_data.csv").then(function(data) {
        // Parse numeric values
        data.forEach(function(d) {
            d.TransactionAmount = +d.TransactionAmount;
        });
        
        // Initialize with FraudFlag view
        let currentData = data;
        let hierarchyLevel = "FraudFlag";
        let currentPath = [];
        
        updateChart();

        function updateChart() {
            // Filter data if needed
            let filteredData = currentData;
            if (currentPath.length > 0) {
                const [filterKey, filterVal] = currentPath[currentPath.length - 1].split(":");
                filteredData = currentData.filter(d => d[filterKey] === filterVal);
            }
            
            // Update the header
            updateHeader();
            
            // Group data by current level
            const groupedData = d3.rollup(
                filteredData,
                v => ({
                    count: v.length,
                    amount: d3.sum(v, d => d.TransactionAmount)
                }),
                d => d[hierarchyLevel]
            );
            
            // Convert to array for pie chart
            const pieData = Array.from(groupedData, ([key, value]) => ({
                key,
                count: value.count,
                value: value.amount
            }));
            
            // Calculate totals
            const totalAmount = d3.sum(pieData, d => d.value);
            const totalCount = d3.sum(pieData, d => d.count);
            
            // Update breadcrumb
            updateBreadcrumb();
            
            // Remove existing chart elements
            chartGroup.selectAll("*").remove();
            
            // Create arcs
            const arcs = pie(pieData);
            
            // Draw arcs
            const arcsGroup = chartGroup.selectAll(".arc")
                .data(arcs)
                .enter()
                .append("g")
                .attr("class", "arc")
                .on("click", function(event, d) {
                    const nextLevel = getNextLevel(hierarchyLevel);
                    if (nextLevel) {
                        currentData = filteredData;
                        currentPath.push(`${hierarchyLevel}:${d.data.key}`);
                        hierarchyLevel = nextLevel;
                        updateChart();
                    }
                })
                .on("mouseover", function(event, d) {
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", .9);
                    tooltip.html(`
                        <strong>${d.data.key}</strong><br>
                        Transactions: ${d.data.count.toLocaleString()}<br>
                        Amount: $${formatNumber(d.data.value)}
                    `)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                })
                .on("mouseout", function() {
                    tooltip.transition()
                        .duration(500)
                        .style("opacity", 0);
                });
            
            // Add pie segments with transition
            arcsGroup.append("path")
                .attr("d", arc)
                .attr("fill", d => {
                    const value = d.data.key;
                    const levelMap = color[hierarchyLevel];
                    return levelMap && levelMap[value] ? levelMap[value] : "#ccc";
                })
                .transition()
                .duration(500)
                .attrTween("d", function(d) {
                    const i = d3.interpolate(this._current || d, d);
                    this._current = i(1);
                    return t => arc(i(t));
                });
            
            // Add labels with connecting lines
            arcsGroup.each(function(d) {
                const centroid = arc.centroid(d);
                const midAngle = d.startAngle + (d.endAngle - d.startAngle) / 2;
                
                // Calculate label position
                const labelX = Math.sin(midAngle) * labelRadius;
                const labelY = -Math.cos(midAngle) * labelRadius;
                
                // Calculate line end position (slightly inside label)
                const lineX = Math.sin(midAngle) * (radius + 10);
                const lineY = -Math.cos(midAngle) * (radius + 10);
                
                // Add connecting line
                chartGroup.append("line")
                    .attr("class", "label-line")
                    .attr("x1", centroid[0])
                    .attr("y1", centroid[1])
                    .attr("x2", lineX)
                    .attr("y2", lineY)
                    .attr("stroke", "#666")
                    .attr("stroke-width", 1);
                
                // Add label
                chartGroup.append("text")
                    .attr("class", "pie-label")
                    .attr("x", labelX)
                    .attr("y", labelY)
                    .attr("text-anchor", midAngle < Math.PI ? "start" : "end")
                    .attr("dy", "0.35em")
                    .text(`${d.data.key} (${d.data.count})`);
            });
            
            // Create total box
            const boxWidth = 180;
            const boxHeight = 80;
            const boxX = width - boxWidth - 20;
            const boxY = height - boxHeight - 20;
            
            svg.append("rect")
                .attr("class", "total-box")
                .attr("x", boxX)
                .attr("y", boxY)
                .attr("width", boxWidth)
                .attr("height", boxHeight)
                .attr("rx", 5)
                .attr("ry", 5);
            
            // Add total labels
            svg.append("text")
                .attr("class", "total-label")
                .attr("x", boxX + 10)
                .attr("y", boxY + 20)
                .text("Total Amount:");
            
            svg.append("text")
                .attr("class", "total-value")
                .attr("x", boxX + 10)
                .attr("y", boxY + 35)
                .text(`$${formatNumber(totalAmount)}`);
            
            svg.append("text")
                .attr("class", "total-label")
                .attr("x", boxX + 10)
                .attr("y", boxY + 55)
                .text("Total Transactions:");
            
            svg.append("text")
                .attr("class", "total-value")
                .attr("x", boxX + 10)
                .attr("y", boxY + 70)
                .text(totalCount.toLocaleString());
        }
        
        function getNextLevel(currentLevel) {
            const hierarchy = ["FraudFlag", "TransactionStatus", "DeviceUsed", "TransactionType"];
            const currentIndex = hierarchy.indexOf(currentLevel);
            return hierarchy[currentIndex + 1];
        }
        
        function getTitle() {
            if (currentPath.length === 0) return `Transaction Amount Distribution by ${hierarchyLevel}`;
            
            const [filterKey, filterVal] = currentPath[currentPath.length - 1].split(":");
            return `Transaction Amount Distribution by ${hierarchyLevel}`;
        }

        function updateHeader() {
            document.getElementById("chart_title").innerText = getTitle();
        }
        
        function updateBreadcrumb() {
            breadcrumb.html("");
            
            // Add root
            breadcrumb.append("span")
                .text("All Transactions")
                .on("click", function() {
                    currentData = data;
                    hierarchyLevel = "FraudFlag";
                    currentPath = [];
                    updateChart();
                });
            
            // Add path segments
            currentPath.forEach((path, i) => {
                const [key, value] = path.split(":");
                
                breadcrumb.append("span")
                    .attr("class", "breadcrumb-separator")
                    .text(">");
                
                breadcrumb.append("span")
                    .text(value)
                    .on("click", function() {
                        currentData = data;
                        hierarchyLevel = key;
                        currentPath = currentPath.slice(0, i);
                        updateChart();
                    });
            });
            
            // Add current level
            if (currentPath.length > 0) {
                breadcrumb.append("span")
                    .attr("class", "breadcrumb-separator")
                    .text(">");
            }
            
            breadcrumb.append("span")
                .text(hierarchyLevel)
                .style("color", "#000")
                .style("cursor", "default");
        }
    });
}

// Initialize the visualization when the page loads
document.addEventListener("DOMContentLoaded", initializeVisualization);