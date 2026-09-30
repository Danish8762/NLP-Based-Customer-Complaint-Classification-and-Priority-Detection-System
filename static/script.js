document.addEventListener('DOMContentLoaded', () => {
    // Form and input elements
    const complaintForm = document.getElementById('complaintForm');
    const complaintInput = document.getElementById('complaintInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnSpinner = document.getElementById('btnSpinner');
    const clearBtn = document.getElementById('clearBtn');
    const charCount = document.getElementById('charCount');
    const wordCount = document.getElementById('wordCount');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');

    // Action buttons
    const copyReportBtn = document.getElementById('copyReportBtn');
    const downloadJsonBtn = document.getElementById('downloadJsonBtn');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const historyTableBody = document.getElementById('historyTableBody');

    // Metric display elements
    const resCategory = document.getElementById('resCategory');
    const resCatConfidence = document.getElementById('resCatConfidence');
    const catProgressBar = document.getElementById('catProgressBar');

    const resPriority = document.getElementById('resPriority');
    const resPrioConfidence = document.getElementById('resPrioConfidence');
    const prioProgressBar = document.getElementById('prioProgressBar');

    const resSentiment = document.getElementById('resSentiment');
    const resCompound = document.getElementById('resCompound');

    const resSeverityScore = document.getElementById('resSeverityScore');
    const resSeverityLabel = document.getElementById('resSeverityLabel');
    const severityProgressBar = document.getElementById('severityProgressBar');

    // Advanced NLP sections
    const keywordsList = document.getElementById('keywordsList');
    const categoryProbsList = document.getElementById('categoryProbsList');
    const priorityProbsList = document.getElementById('priorityProbsList');

    // NLP Inspector elements
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const inspectorTokens = document.getElementById('inspectorTokens');
    const inspectorStopwords = document.getElementById('inspectorStopwords');
    const inspectorLemmas = document.getElementById('inspectorLemmas');
    const statChars = document.getElementById('statChars');
    const statWords = document.getElementById('statWords');
    const statUnique = document.getElementById('statUnique');
    const statDiversity = document.getElementById('statDiversity');
    const resPreprocessed = document.getElementById('resPreprocessed');

    // Recommendations
    const recDepartment = document.getElementById('recDepartment');
    const recSLA = document.getElementById('recSLA');
    const recAction = document.getElementById('recAction');

    // Sample buttons
    const sampleButtons = document.querySelectorAll('.sample-btn');

    // State storage
    let currentAnalysisData = null;
    let triageHistory = [];

    // Live typing statistics
    function updateTextStats() {
        const text = complaintInput.value.trim();
        const chars = complaintInput.value.length;
        const words = text ? text.split(/\s+/).length : 0;
        charCount.textContent = `${chars} character${chars === 1 ? '' : 's'}`;
        wordCount.textContent = `${words} word${words === 1 ? '' : 's'}`;
    }

    complaintInput.addEventListener('input', () => {
        updateTextStats();
        hideError();
    });

    // Sample button click handler
    sampleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const sampleText = btn.getAttribute('data-text');
            complaintInput.value = sampleText;
            updateTextStats();
            hideError();
            complaintInput.focus();
        });
    });

    // Clear input button
    clearBtn.addEventListener('click', () => {
        complaintInput.value = '';
        updateTextStats();
        hideError();
        resultsSection.style.display = 'none';
        complaintInput.focus();
    });

    // Helper alerts
    function showError(msg) {
        errorMessage.textContent = msg;
        errorAlert.style.display = 'flex';
        resultsSection.style.display = 'none';
    }

    function hideError() {
        errorAlert.style.display = 'none';
    }

    function setLoading(isLoading) {
        if (isLoading) {
            analyzeBtn.disabled = true;
            btnSpinner.style.display = 'inline-block';
            loadingIndicator.style.display = 'block';
            resultsSection.style.display = 'none';
            hideError();
        } else {
            analyzeBtn.disabled = false;
            btnSpinner.style.display = 'none';
            loadingIndicator.style.display = 'none';
        }
    }

    // Inspector Tab Switching
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const activePane = document.getElementById(targetTab);
            if (activePane) {
                activePane.classList.add('active');
            }
        });
    });

    // Submit handler
    complaintForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const complaintText = complaintInput.value.trim();

        if (!complaintText) {
            showError('Please enter a complaint before analyzing.');
            complaintInput.focus();
            return;
        }

        if (complaintText.length < 5) {
            showError('Complaint is too short. Please provide a more descriptive sentence.');
            complaintInput.focus();
            return;
        }

        setLoading(true);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ complaint: complaintText })
            });

            const data = await response.json();

            if (!response.ok) {
                showError(data.error || 'Server error occurred during processing.');
                setLoading(false);
                return;
            }

            currentAnalysisData = {
                raw_text: complaintText,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                ...data
            };

            // 1. Render Core Metrics
            renderCoreMetrics(data);

            // 2. Render Explainable AI Salient Keywords
            renderKeywords(data.top_keywords || []);

            // 3. Render Multi-Class Probability Distributions
            renderDistributions(data.category_distribution || [], data.priority_distribution || []);

            // 4. Render Step-by-Step NLP Inspector
            renderNlpInspector(data.nlp_details, data.preprocessed_text);

            // 5. Render Helpdesk Recommendations
            renderRecommendations(data.helpdesk_recommendation);

            // 6. Record in Triage History Log
            addToHistory(currentAnalysisData);

            // Show results and scroll smoothly
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } catch (err) {
            console.error('Fetch error:', err);
            showError('Unable to connect to Flask server. Please make sure python app.py is running.');
        } finally {
            setLoading(false);
        }
    });

    // Render Core Metrics
    function renderCoreMetrics(data) {
        // Category
        resCategory.textContent = data.category;
        const catConf = (data.confidence * 100).toFixed(1);
        resCatConfidence.textContent = `${catConf}%`;
        catProgressBar.style.width = `${Math.min(catConf, 100)}%`;

        // Priority
        resPriority.textContent = data.priority.toUpperCase();
        resPriority.className = 'priority-badge';
        resPriority.classList.add(`priority-${data.priority.toLowerCase()}`);
        const prioConf = (data.priority_confidence * 100).toFixed(1);
        resPrioConfidence.textContent = `${prioConf}%`;
        prioProgressBar.style.width = `${Math.min(prioConf, 100)}%`;

        // Sentiment
        resSentiment.textContent = data.sentiment.toUpperCase();
        resSentiment.className = 'sentiment-badge';
        resSentiment.classList.add(`sentiment-${data.sentiment.toLowerCase()}`);
        resCompound.textContent = Number(data.compound_score).toFixed(2);

        // Severity Score
        const sev = data.severity_score || 50;
        resSeverityScore.textContent = sev;
        severityProgressBar.style.width = `${sev}%`;

        if (sev >= 75) {
            resSeverityLabel.textContent = 'Critical Urgent Action';
            resSeverityLabel.style.color = 'var(--color-high)';
        } else if (sev >= 45) {
            resSeverityLabel.textContent = 'Moderate Priority Ticket';
            resSeverityLabel.style.color = 'var(--color-medium)';
        } else {
            resSeverityLabel.textContent = 'Low Urgency / Routine';
            resSeverityLabel.style.color = 'var(--color-low)';
        }
    }

    // Render Salient Keywords (Explainable AI)
    function renderKeywords(keywords) {
        keywordsList.innerHTML = '';
        if (!keywords || keywords.length === 0) {
            keywordsList.innerHTML = '<span class="pane-caption">No specific high-weighted terms identified.</span>';
            return;
        }

        keywords.forEach(kw => {
            const pill = document.createElement('div');
            pill.className = 'keyword-pill';
            const pct = Math.min(Math.round(kw.weight * 100 * 1.5), 100);

            pill.innerHTML = `
                <div class="kw-term">${escapeHtml(kw.term)}</div>
                <div class="kw-meta">
                    <span>TF-IDF Score</span>
                    <strong>${kw.weight.toFixed(3)}</strong>
                </div>
                <div class="kw-track">
                    <div class="kw-bar" style="width: ${pct}%;"></div>
                </div>
            `;
            keywordsList.appendChild(pill);
        });
    }

    // Render Probability Distributions
    function renderDistributions(catDist, prioDist) {
        // Categories
        categoryProbsList.innerHTML = '';
        catDist.forEach((item, idx) => {
            const pct = (item.probability * 100).toFixed(1);
            const isTop = idx === 0;
            const row = document.createElement('div');
            row.className = 'prob-row';
            row.innerHTML = `
                <div class="prob-row-header">
                    <span>${escapeHtml(item.name)}</span>
                    <strong>${pct}%</strong>
                </div>
                <div class="prob-track">
                    <div class="prob-fill ${isTop ? 'prob-fill-top' : ''}" style="width: ${pct}%;"></div>
                </div>
            `;
            categoryProbsList.appendChild(row);
        });

        // Priorities
        priorityProbsList.innerHTML = '';
        prioDist.forEach((item, idx) => {
            const pct = (item.probability * 100).toFixed(1);
            const isTop = idx === 0;
            const row = document.createElement('div');
            row.className = 'prob-row';
            row.innerHTML = `
                <div class="prob-row-header">
                    <span>${escapeHtml(item.name)} Priority</span>
                    <strong>${pct}%</strong>
                </div>
                <div class="prob-track">
                    <div class="prob-fill ${isTop ? 'prob-fill-top' : ''}" style="width: ${pct}%;"></div>
                </div>
            `;
            priorityProbsList.appendChild(row);
        });
    }

    // Render Step-by-Step NLP Inspector
    function renderNlpInspector(nlp, cleanText) {
        resPreprocessed.textContent = cleanText || '(Empty after preprocessing)';

        if (!nlp) return;

        // Tab 1: Tokens
        inspectorTokens.innerHTML = '';
        (nlp.tokens || []).forEach(tok => {
            const chip = document.createElement('span');
            chip.className = 'token-chip';
            chip.textContent = tok;
            inspectorTokens.appendChild(chip);
        });

        // Tab 2: Stopwords
        inspectorStopwords.innerHTML = '';
        if (nlp.stopwords_removed && nlp.stopwords_removed.length > 0) {
            nlp.stopwords_removed.forEach(tok => {
                const chip = document.createElement('span');
                chip.className = 'token-chip token-stopword';
                chip.textContent = tok;
                inspectorStopwords.appendChild(chip);
            });
        } else {
            inspectorStopwords.innerHTML = '<span class="pane-caption">No stop-words detected in this text.</span>';
        }

        // Tab 3: Lemmas
        inspectorLemmas.innerHTML = '';
        if (nlp.lemmas && nlp.lemmas.length > 0) {
            nlp.lemmas.forEach(pair => {
                const item = document.createElement('div');
                item.className = 'lemma-chip';
                item.innerHTML = `
                    <span class="lemma-orig">${escapeHtml(pair.original)}</span>
                    <span class="lemma-arrow">→</span>
                    <span class="lemma-root">${escapeHtml(pair.lemma)}</span>
                `;
                inspectorLemmas.appendChild(item);
            });
        } else {
            inspectorLemmas.innerHTML = '<span class="pane-caption">No lemmatized tokens available.</span>';
        }

        // Tab 4: Stats
        const stats = nlp.stats || {};
        statChars.textContent = stats.total_chars || 0;
        statWords.textContent = stats.total_words || 0;
        statUnique.textContent = stats.unique_words || 0;
        statDiversity.textContent = `${stats.lexical_diversity || 0}%`;
    }

    // Render Helpdesk Recommendations
    function renderRecommendations(rec) {
        if (!rec) return;
        recDepartment.textContent = rec.department || '-';
        recSLA.textContent = rec.target_sla || '-';
        recAction.textContent = rec.action_plan || '-';
    }

    // Add to Session History
    function addToHistory(item) {
        triageHistory.unshift(item);
        if (triageHistory.length > 15) {
            triageHistory.pop();
        }
        renderHistoryTable();
    }

    function renderHistoryTable() {
        if (triageHistory.length === 0) {
            historyTableBody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="7">No complaints analyzed yet in this session. Analyze a complaint to see it logged here!</td>
                </tr>
            `;
            return;
        }

        historyTableBody.innerHTML = '';
        triageHistory.forEach((row, idx) => {
            const tr = document.createElement('tr');
            const prioClass = `priority-${row.priority.toLowerCase()}`;
            const sentClass = `sentiment-${row.sentiment.toLowerCase()}`;

            tr.innerHTML = `
                <td><code>${row.timestamp}</code></td>
                <td class="history-text" title="${escapeHtml(row.raw_text)}">${escapeHtml(row.raw_text)}</td>
                <td><strong>${escapeHtml(row.category)}</strong></td>
                <td><span class="pill-sm ${prioClass}">${row.priority.toUpperCase()}</span></td>
                <td><span class="pill-sm ${sentClass}">${row.sentiment.toUpperCase()}</span></td>
                <td><strong>${row.severity_score}/100</strong></td>
                <td>
                    <button type="button" class="btn btn-secondary btn-sm reload-btn" data-index="${idx}">Reload</button>
                </td>
            `;
            historyTableBody.appendChild(tr);
        });

        // Bind reload buttons
        document.querySelectorAll('.reload-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = parseInt(btn.getAttribute('data-index'), 10);
                const item = triageHistory[idx];
                if (item) {
                    complaintInput.value = item.raw_text;
                    updateTextStats();
                    renderCoreMetrics(item);
                    renderKeywords(item.top_keywords || []);
                    renderDistributions(item.category_distribution || [], item.priority_distribution || []);
                    renderNlpInspector(item.nlp_details, item.preprocessed_text);
                    renderRecommendations(item.helpdesk_recommendation);
                    resultsSection.style.display = 'block';
                    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }

    // Clear history
    clearHistoryBtn.addEventListener('click', () => {
        triageHistory = [];
        renderHistoryTable();
    });

    // Copy Summary Report
    copyReportBtn.addEventListener('click', () => {
        if (!currentAnalysisData) return;

        const summary = `
[CUSTOMER COMPLAINT TRIAGE REPORT]
Timestamp: ${currentAnalysisData.timestamp}
Original Complaint: "${currentAnalysisData.raw_text}"

• Predicted Category : ${currentAnalysisData.category} (Confidence: ${(currentAnalysisData.confidence * 100).toFixed(1)}%)
• Urgency Priority   : ${currentAnalysisData.priority.toUpperCase()} (Confidence: ${(currentAnalysisData.priority_confidence * 100).toFixed(1)}%)
• Customer Sentiment : ${currentAnalysisData.sentiment.toUpperCase()} (Compound: ${currentAnalysisData.compound_score})
• Severity Score     : ${currentAnalysisData.severity_score} / 100
• Preprocessed Tokens: ${currentAnalysisData.preprocessed_text}

[RECOMMENDATION]
• Department : ${currentAnalysisData.helpdesk_recommendation.department}
• Target SLA : ${currentAnalysisData.helpdesk_recommendation.target_sla}
• Action Plan: ${currentAnalysisData.helpdesk_recommendation.action_plan}
        `.trim();

        navigator.clipboard.writeText(summary).then(() => {
            const originalText = copyReportBtn.innerHTML;
            copyReportBtn.innerHTML = '✓ Copied!';
            setTimeout(() => {
                copyReportBtn.innerHTML = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Copy failed:', err);
        });
    });

    // Download JSON Report
    downloadJsonBtn.addEventListener('click', () => {
        if (!currentAnalysisData) return;

        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentAnalysisData, null, 2));
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute("href", dataStr);
        downloadAnchor.setAttribute("download", `complaint_analysis_${Date.now()}.json`);
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        downloadAnchor.remove();
    });

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Initialize stats
    updateTextStats();
});
