document.addEventListener('DOMContentLoaded', function() {
    // 要素の取得
    const navLinks = document.querySelectorAll('.nav-link');
    const apiSections = document.querySelectorAll('.api-section');
    const searchBox = document.getElementById('searchBox');

    // ナビゲーション機能
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // アクティブリンクの更新
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // セクションの表示切り替え
            const category = this.dataset.category;
            showSection(category);
        });
    });

    // セクション表示関数
    function showSection(targetCategory) {
        apiSections.forEach(section => {
            if (section.id === 'intro') {
                section.style.display = 'none';
            } else if (section.dataset.category === targetCategory) {
                section.style.display = 'block';
                // スムーズスクロール
                section.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            } else {
                section.style.display = 'none';
            }
        });
    }

    // 検索機能
    let searchTimeout;
    searchBox.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const query = this.value.toLowerCase().trim();
            
            if (query === '') {
                // 検索クエリが空の場合、全てのハイライトを削除
                clearHighlights();
                showAllSections();
                removeNoResults();
                return;
            }
            
            searchAPI(query);
        }, 300);
    });

    // API検索関数
    function searchAPI(query) {
        const allMethods = document.querySelectorAll('.api-method');
        let hasResults = false;
        
        // 全てのセクションを非表示にし、ハイライトをクリア
        hideAllSections();
        clearHighlights();
        removeNoResults();
        
        allMethods.forEach(method => {
            const methodName = method.querySelector('h3').textContent.toLowerCase();
            const description = method.querySelector('.description');
            const descriptionText = description ? description.textContent.toLowerCase() : '';
            const parentSection = method.closest('.api-section');
            
            if (methodName.includes(query) || descriptionText.includes(query)) {
                // マッチした場合、親セクションを表示
                parentSection.style.display = 'block';
                hasResults = true;
                
                // ハイライト表示
                highlightText(method, query);
                
                // メソッドを強調表示
                method.style.border = '2px solid #ff0000';
                method.style.backgroundColor = '#fff5f5';
            } else {
                // マッチしない場合はデフォルトスタイルに戻す
                method.style.border = '';
                method.style.backgroundColor = '';
            }
        });
        
        // 検索結果がない場合
        if (!hasResults) {
            showNoResults(query);
        }
    }

    // テキストハイライト関数
    function highlightText(element, query) {
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        const textNodes = [];
        let node;
        
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }
        
        textNodes.forEach(textNode => {
            const text = textNode.textContent;
            const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
            
            if (regex.test(text)) {
                const highlightedText = text.replace(regex, '<span class="highlight">$1</span>');
                const span = document.createElement('span');
                span.innerHTML = highlightedText;
                textNode.parentNode.replaceChild(span, textNode);
            }
        });
    }

    // 正規表現エスケープ関数
    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // ハイライトクリア関数
    function clearHighlights() {
        const highlights = document.querySelectorAll('.highlight');
        highlights.forEach(highlight => {
            const parent = highlight.parentNode;
            parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
            parent.normalize();
        });
        
        // メソッドの強調表示もクリア
        const methods = document.querySelectorAll('.api-method');
        methods.forEach(method => {
            method.style.border = '';
            method.style.backgroundColor = '';
        });
    }

    // 全セクション表示関数
    function showAllSections() {
        document.getElementById('intro').style.display = 'block';
        apiSections.forEach(section => {
            if (section.id !== 'intro') {
                section.style.display = 'none';
            }
        });
    }

    // 全セクション非表示関数
    function hideAllSections() {
        apiSections.forEach(section => {
            section.style.display = 'none';
        });
    }

    // 検索結果なし表示関数
    function showNoResults(query) {
        const content = document.querySelector('.content');
        const noResultsDiv = document.getElementById('no-results') || document.createElement('div');
        
        noResultsDiv.id = 'no-results';
        noResultsDiv.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: #666;">
                <h3>「${query}」の検索結果が見つかりませんでした</h3>
                <p>以下をお試しください:</p>
                <ul style="text-align: left; display: inline-block; margin-top: 1rem;">
                    <li>キーワードのスペルを確認してください</li>
                    <li>より一般的なキーワードで検索してください</li>
                    <li>異なるキーワードで検索してください</li>
                    <li>左のナビゲーションからカテゴリを選択してください</li>
                </ul>
                <div style="margin-top: 2rem;">
                    <strong>🔍 検索のヒント:</strong><br>
                    「video」「search」「playlist」「channel」「comment」などの基本的なキーワードをお試しください
                </div>
            </div>
        `;
        
        if (!document.getElementById('no-results')) {
            content.appendChild(noResultsDiv);
        }
        
        noResultsDiv.style.display = 'block';
    }

    // 検索結果なし要素の削除
    function removeNoResults() {
        const noResults = document.getElementById('no-results');
        if (noResults) {
            noResults.style.display = 'none';
        }
    }

    // スムーズスクロール機能の改善
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // 初期表示設定
    document.getElementById('intro').style.display = 'block';

    // キーボードショートカット
    document.addEventListener('keydown', function(e) {
        // Ctrl+K または Cmd+K で検索ボックスにフォーカス
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            searchBox.focus();
            searchBox.select();
        }
        
        // Escape で検索をクリア
        if (e.key === 'Escape' && document.activeElement === searchBox) {
            searchBox.value = '';
            clearHighlights();
            showAllSections();
            removeNoResults();
        }
    });

    // 統計情報の更新
    function updateStats() {
        const statsContainer = document.querySelector('.stats-summary ul');
        const methodCounts = {};
        
        // カテゴリ別メソッド数をカウント
        apiSections.forEach(section => {
            if (section.id !== 'intro') {
                const category = section.id;
                const methods = section.querySelectorAll('.api-method');
                methodCounts[category] = methods.length;
            }
        });

        // 統計を更新
        const totalMethods = Object.values(methodCounts).reduce((sum, count) => sum + count, 0);
        
        if (statsContainer) {
            statsContainer.innerHTML = `
                <li>基本クラス: ${methodCounts.basic || 0}メソッド</li>
                <li>基本情報取得: ${methodCounts.info || 0}メソッド</li>
                <li>検索機能: ${methodCounts.search || 0}メソッド</li>
                <li>リスト取得: ${methodCounts.list || 0}メソッド</li>
                <li>ページネーション: ${methodCounts.pagination || 0}メソッド</li>
                <li>簡略化メソッド: ${methodCounts.simple || 0}メソッド</li>
                <li>ヘルパーメソッド: ${methodCounts.helper || 0}メソッド</li>
                <li>プレイリスト管理: ${methodCounts.playlist || 0}メソッド</li>
                <li>その他機能: ${totalMethods - (methodCounts.basic + methodCounts.info + methodCounts.search + methodCounts.list + methodCounts.pagination + methodCounts.simple + methodCounts.helper + methodCounts.playlist || 0)}メソッド</li>
            `;
            
            const totalElement = statsContainer.parentNode.querySelector('p strong');
            if (totalElement) {
                totalElement.textContent = `合計: ${totalMethods}の実装済みメソッド`;
            }
        }
    }

    // 統計情報を初期化時に更新
    updateStats();

    // パフォーマンス監視
    console.log('🚀 YouTube API リファレンス サイト初期化完了');
    console.log(`📊 総メソッド数: ${document.querySelectorAll('.api-method').length}`);
    console.log(`📂 カテゴリ数: ${document.querySelectorAll('.api-section[data-category]').length}`);
});