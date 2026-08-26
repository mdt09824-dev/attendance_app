<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attendance E-Khata</title>
    <style>
        :root {
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #333333;
            --primary-color: #1a1a2e;
            --accent-color: #0f3460;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .container {
            width: 100%;
            max-width: 480px;
            padding: 15px;
            box-sizing: border-box;
            margin-bottom: 70px;
        }

        .header {
            text-align: center;
            margin-bottom: 20px;
        }

        .header h1 {
            font-size: 24px;
            color: var(--primary-color);
            margin: 10px 0 0;
        }

        /* Navigation Bar */
        .nav-bar {
            position: fixed;
            bottom: 0;
            width: 100%;
            max-width: 480px;
            background: var(--primary-color);
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
        }

        .nav-item {
            color: #ffffff;
            background: none;
            border: none;
            font-size: 14px;
            cursor: pointer;
            padding: 5px 10px;
            border-radius: 5px;
        }

        .nav-item.active {
            background: var(--accent-color);
            font-weight: bold;
        }

        /* Views */
        .view-section {
            display: none;
        }

        .view-section.active {
            display: block;
        }

        /* Tables & Lists */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            background: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-top: 10px;
        }

        .data-table th, .data-table td {
            padding: 12px;
            text-align: center;
            font-size: 14px;
            border-bottom: 1px solid #eee;
            color: var(--text-color); /* লেখা স্পষ্ট করার জন্য কালো কালার দেওয়া হয়েছে */
        }

        .data-table th {
            background-color: var(--primary-color);
            color: #ffffff;
        }

        /* History Accordion */
        .history-card {
            background: var(--card-bg);
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            overflow: hidden;
        }

        .history-header {
            background: var(--primary-color);
            color: white;
            padding: 12px 15px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
        }

        .history-body {
            padding: 10px;
            display: none;
            background: #ffffff;
        }

        .history-body.show {
            display: block;
        }

        .status-badge {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .present { background: #d4edda; color: #155724; }
        .absent { background: #f8d7da; color: #721c24; }
        .leave { background: #fff3cd; color: #856404; }

        /* General UI elements */
        .section-title {
            font-size: 18px;
            margin: 15px 0 10px;
            color: var(--primary-color);
            display: flex;
            align-items: center;
            gap: 8px;
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📚 Attendance E-Khata</h1>
        </div>

        <!-- 1. Main Home View (আগের ইন্টারফেস অপরিবর্তিত রাখা হয়েছে) -->
        <div id="homeView" class="view-section active">
            <div class="section-title">📅 Select Date: 2026 / 08 / 26</div>
            <div style="background: #22252a; color: white; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                2026 / 08 / 26
            </div>
            
            <!-- Summary boxes -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 15px;">
                <div style="background: #28a745; color: white; padding: 10px; border-radius: 8px; text-align: center;"><small>Present</small><br><strong>16</strong></div>
                <div style="background: #fd7e14; color: white; padding: 10px; border-radius: 8px; text-align: center;"><small>Leave</small><br><strong>1</strong></div>
                <div style="background: #dc3545; color: white; padding: 10px; border-radius: 8px; text-align: center;"><small>Absent</small><br><strong>0</strong></div>
                <div style="background: #007bff; color: white; padding: 10px; border-radius: 8px; text-align: center;"><small>Total Due</small><br><strong>20Tk</strong></div>
            </div>

            <!-- Student List Sample -->
            <div style="background: white; padding: 12px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <span style="color: var(--text-color);">👤 Rounak</span>
                <span class="status-badge present">PRESENT</span>
            </div>
        </div>

        <!-- 2. Total Due / Fine List View (আপডেটকৃত) -->
        <div id="fineView" class="view-section">
            <div class="section-title">💰 Total Due / Fine List</div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Student Name</th>
                        <th>Date</th>
                        <th>Total Fine</th>
                        <th>Paid</th>
                        <th>Due</th>
                    </tr>
                </thead>
                <tbody id="fineTableBody">
                    <!-- JavaScript দিয়ে ডাটা লোড হবে -->
                </tbody>
            </table>
        </div>

        <!-- 3. Attendance History View (আপডেটকৃত) -->
        <div id="historyView" class="view-section">
            <div class="section-title">📊 Attendance History</div>
            <div id="historyContainer">
                <!-- JavaScript দিয়ে অ্যাকর্ডিয়ন হিস্ট্রি তৈরি হবে -->
            </div>
        </div>
    </div>

    <!-- Bottom Navigation Bar -->
    <div class="nav-bar">
        <button class="nav-item active" onclick="switchView('homeView', this)">Home</button>
        <button class="nav-item" onclick="switchView('fineView', this)">Fine List</button>
        <button class="nav-item" onclick="switchView('historyView', this)">History</button>
    </div>

    <script>
        // স্যাম্পল ডাটা (Fine & History এর জন্য)
        const fineData = [
            { name: "Nirob", date: "2026-08-25", total: "20 Tk", paid: "0 Tk", due: "20 Tk" },
            { name: "Jahidul", date: "2026-08-24", total: "20 Tk", paid: "0 Tk", due: "20 Tk" },
            { name: "Tabassum", date: "2026-08-23", total: "50 Tk", paid: "40 Tk", due: "10 Tk" }
        ];

        const historyData = [
            {
                date: "26-08-2026 -- Present: 16 | Leave: 1 | Absent: 0",
                students: [
                    { name: "Rounak", status: "PRESENT" },
                    { name: "Nirob", status: "LEAVE" },
                    { name: "Jahidul", status: "PRESENT" }
                ]
            },
            {
                date: "25-08-2026 -- Present: 15 | Leave: 0 | Absent: 2",
                students: [
                    { name: "Rounak", status: "PRESENT" },
                    { name: "Nirob", status: "ABSENT" },
                    { name: "Jahidul", status: "PRESENT" }
                ]
            }
        ];

        // পেজ সুইচ করার ফাংশন
        function switchView(viewId, element) {
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            
            document.getElementById(viewId).classList.add('active');
            element.classList.add('active');
        }

        // ফাইন লিস্ট রেন্ডার করা
        function loadFineList() {
            const tbody = document.getElementById('fineTableBody');
            tbody.innerHTML = '';
            fineData.forEach(item => {
                tbody.innerHTML += `
                    <tr>
                        <td>${item.name}</td>
                        <td>${item.date}</td>
                        <td>${item.total}</td>
                        <td>${item.paid}</td>
                        <td>${item.due}</td>
                    </tr>
                `;
            });
        }

        // হিস্ট্রি লিস্ট রেন্ডার করা (অ্যাকর্ডিয়ন সহ)
        function loadHistory() {
            const container = document.getElementById('historyContainer');
            container.innerHTML = '';
            historyData.forEach((hist, index) => {
                let studentRows = hist.students.map(s => `
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0;">
                        <span>${s.name}</span>
                        <span class="status-badge ${s.status.toLowerCase()}">${s.status}</span>
                    </div>
                `).join('');

                container.innerHTML += `
                    <div class="history-card">
                        <div class="history-header" onclick="toggleAccordion(${index})">
                            <span>${hist.date}</span>
                            <span>▼</span>
                        </div>
                        <div class="history-body" id="hist-body-${index}">
                            ${studentRows}
                        </div>
                    </div>
                `;
            });
        }

        // অ্যাকর্ডিয়ন টগল করার ফাংশন
        function toggleAccordion(index) {
            const body = document.getElementById(`hist-body-${index}`);
            body.classList.toggle('show');
        }

        // ইনিশিয়ালাইজেশন
        window.onload = function() {
            loadFineList();
            loadHistory();
        };
    </script>
</body>
</html>
