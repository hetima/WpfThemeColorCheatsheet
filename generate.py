import xml.etree.ElementTree as ET
import re
import json
import os


class Xaml:
    def __init__(self, path: str):
        self.path = path
        self.colors = {}
        self.color_brushes = {}
        self._parse_xaml()

    def _parse_xaml(self):
        """XAMLファイルを解析してColorとSolidColorBrushを取得する"""
        tree = ET.parse(self.path)
        root = tree.getroot()

        # 名前空間の定義
        # XAMLのデフォルト名前空間
        default_ns = 'http://schemas.microsoft.com/winfx/2006/xaml/presentation'
        x_ns = 'http://schemas.microsoft.com/winfx/2006/xaml'

        # 1. Color要素を取得（デフォルト名前空間を使用）
        for color_elem in root.findall(f'{{{default_ns}}}Color'):
            name = color_elem.get(f'{{{x_ns}}}Key')
            value = color_elem.text
            if name and value:
                self.colors[name] = value

        # 2. SolidColorBrush要素を取得（デフォルト名前空間を使用）
        for brush_elem in root.findall(f'{{{default_ns}}}SolidColorBrush'):
            name = brush_elem.get(f'{{{x_ns}}}Key')
            color_attr = brush_elem.get('Color')
            if name and color_attr:
                # Color="{StaticResource ControlFillColorDisabled}" 形式からキーを抽出
                match = re.search(r'StaticResource\s+(\w+)', color_attr)
                if match:
                    color_key = match.group(1)
                    # color辞書から値を取得
                    color_value = self.colors.get(color_key)
                    if color_value:
                        self.color_brushes[name] = color_value



class Generator:
    """main class"""

    def __init__(self):
        self.light_xaml = Xaml("Light.xaml")
        self.dark_xaml = Xaml("Dark.xaml")
        self.brushes = {}

    def hex_to_rgba(self, hex_color):
        """C#の色指定（#RRGGBB または #AARRGGBB）をrgba形式に変換する"""
        if not hex_color or len(hex_color) < 7:
            return None, None

        hex_color = hex_color.strip()

        if len(hex_color) == 7:  # #RRGGBB
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            a = 1.0
        elif len(hex_color) == 9:  # #AARRGGBB
            a = int(hex_color[1:3], 16) / 255
            r = int(hex_color[3:5], 16)
            g = int(hex_color[5:7], 16)
            b = int(hex_color[7:9], 16)
        else:
            return None, None

        rgba_value = f'rgba({r}, {g}, {b}, {a:.3f})'
        return rgba_value, a

    def calculate_brightness(self, hex_color):
        """色の明るさを計算する（輝度公式を使用）"""
        if not hex_color or len(hex_color) < 7:
            return 0

        hex_color = hex_color.strip()

        if len(hex_color) == 9:  # #AARRGGBB（透明色）
            # 透明色の場合、背景色（#FAFAFA）と合成
            alpha = int(hex_color[1:3], 16) / 255
            fg_r = int(hex_color[3:5], 16)
            fg_g = int(hex_color[5:7], 16)
            fg_b = int(hex_color[7:9], 16)

            # 背景色 #FAFAFA (RGB: 250, 250, 250)
            bg_r = 250
            bg_g = 250
            bg_b = 250

            # Alpha Blending: result = foreground * alpha + background * (1 - alpha)
            r = fg_r * alpha + bg_r * (1 - alpha)
            g = fg_g * alpha + bg_g * (1 - alpha)
            b = fg_b * alpha + bg_b * (1 - alpha)
        elif len(hex_color) == 7:  # #RRGGBB
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
        else:
            return 0

        # 輝度公式: 0.299*R + 0.587*G + 0.114*B
        return 0.299 * r + 0.587 * g + 0.114 * b

    def construct_brushes(self):
        """light_xamlのcolor_brushesをループして、lightとdarkの値を持つ辞書を作成する"""
        for name, light_value in self.light_xaml.color_brushes.items():
            # dark_xamlから同名のキーの値を取得
            dark_value = self.dark_xaml.color_brushes.get(name)

            # HTML用のrgba形式に変換
            light_rgba, light_alpha = self.hex_to_rgba(light_value)
            dark_rgba, dark_alpha = self.hex_to_rgba(dark_value)

            # Lightテーマの色の明るさを計算
            light_brightness = self.calculate_brightness(light_value)

            self.brushes[name] = {
                "light_value": light_value,
                "dark_value": dark_value,
                "light_value_html": light_rgba,
                "dark_value_html": dark_rgba,
                "light_alpha": light_alpha,
                "dark_alpha": dark_alpha,
                "light_brightness": light_brightness
            }

    def run(self):
        """メイン処理を実行"""
        self.construct_brushes()
        self.generate_html()

    def generate_html(self):
        """index.htmlを生成する"""
        # brushesデータをJSONに変換
        brushes_json = json.dumps(self.brushes)

        html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WPF Theme Color Cheatsheet</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f5f5f5;
            padding-top: 100px;
        }}

        header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background-color: #ffffff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            padding: 12px 24px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .header-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .header-bottom {{
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }}

        h1 {{
            font-size: 20px;
            font-weight: 600;
            color: #333;
            margin: 0;
        }}

        #search-input {{
            width: 100%;
            padding: 10px 36px 10px 16px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
            box-sizing: border-box;
        }}

        #search-input:focus {{
            border-color: #0078d4;
        }}

        .search-container {{
            position: relative;
            flex: 1;
            max-width: 480px;
            min-width: 200px;
        }}

        .clear-btn {{
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
            border: none;
            background: none;
            cursor: pointer;
            font-size: 18px;
            color: #999;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 0;
            line-height: 1;
        }}

        .clear-btn:hover {{
            color: #666;
        }}

        .sort-buttons {{
            display: flex;
            gap: 8px;
            margin-left: 16px;
        }}

        .sort-btn {{
            padding: 8px 16px;
            border: 1px solid #ddd;
            border-radius: 6px;
            background-color: #fff;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .sort-btn:hover {{
            background-color: #f5f5f5;
            border-color: #ccc;
        }}

        .sort-btn.active {{
            background-color: #0078d4;
            color: #fff;
            border-color: #0078d4;
        }}

        .github-link {{
            font-size: 12px;
            color: #666;
            text-decoration: none;
            margin-left: 16px;
            transition: color 0.2s;
        }}

        .github-link:hover {{
            color: #0078d4;
        }}

        .copy-checkbox {{
            display: flex;
            align-items: center;
            gap: 6px;
            margin-left: 16px;
            font-size: 13px;
            color: #666;
            cursor: pointer;
            user-select: none;
        }}

        .copy-checkbox input {{
            width: 16px;
            height: 16px;
            cursor: pointer;
        }}

        .copy-checkbox span {{
            white-space: nowrap;
        }}

        main {{
            padding: 24px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        #grid-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }}

        .brush-card {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            transition: box-shadow 0.2s;
            cursor: pointer;
        }}

        .brush-card:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}

        .brush-name {{
            font-size: 14px;
            font-weight: 500;
            color: #333;
            margin-bottom: 12px;
            word-break: break-all;
        }}

        .color-preview {{
            display: flex;
            gap: 8px;
        }}

        .color-item {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 4px;
            padding: 8px;
            border-radius: 4px;
        }}

        .color-item.light {{
            background-color: #FAFAFA;
        }}

        .color-item.dark {{
            background-color: #202020;
        }}

        .color-box {{
            height: 60px;
            border-radius: 4px;
            position: relative;
            overflow: hidden;
        }}

        .color-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
        }}

        .color-value {{
            font-size: 11px;
            font-family: monospace;
            color: #222;
            text-align: center;
            word-break: break-all;
        }}

        .color-label {{
            font-size: 11px;
            color: #222;
            text-align: center;
        }}

        .color-item.dark .color-label {{
            color: #EEE;
        }}

        .color-item.dark .color-value {{
            color: #EEE;
        }}

        .no-results {{
            text-align: center;
            color: #666;
            padding: 40px;
            font-size: 14px;
        }}

        .toast {{
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            background-color: #333;
            color: #fff;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s;
            z-index: 1000;
        }}

        .toast.show {{
            opacity: 1;
            visibility: visible;
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-top">
            <h1>WPF Theme Color Cheatsheet</h1>
            <a href="https://github.com/hetima/WpfThemeColorCheatsheet" class="github-link" target="_blank" rel="noopener noreferrer">GitHub</a>
        </div>
        <div class="header-bottom">
            <div class="search-container">
                <input type="text" id="search-input" placeholder="Search Brushes..." />
                <button class="clear-btn" id="clear-btn" title="Clear">×</button>
            </div>
            <div class="sort-buttons">
                <button class="sort-btn active" id="sort-name" data-sort="name">Sort by Name</button>
                <button class="sort-btn" id="sort-color" data-sort="color">Sort by Color</button>
            </div>
            <label class="copy-checkbox">
                <input type="checkbox" id="copy-dynamic-resource" />
                <span>Copy as {{DynamicResource Name}}</span>
            </label>
        </div>
    </header>

    <main>
        <div id="grid-container"></div>
    </main>

    <div id="toast" class="toast"></div>

    <script>
        const brushes = {brushes_json};
        let currentSort = 'name';

        // 検索入力とクリアボタンの設定
        const searchInput = document.getElementById('search-input');
        const clearBtn = document.getElementById('clear-btn');

        // 入力値に応じてクリアボタンの表示/非表示を切り替え
        searchInput.addEventListener('input', (e) => {{
            clearBtn.style.display = searchInput.value ? 'flex' : 'none';
            renderBrushes(searchInput.value);
        }});

        // クリアボタンクリックで検索をクリア
        clearBtn.addEventListener('click', () => {{
            searchInput.value = '';
            clearBtn.style.display = 'none';
            renderBrushes();
            searchInput.focus();
        }});

        // ESCキーで検索をクリア
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape' && searchInput.value) {{
                searchInput.value = '';
                clearBtn.style.display = 'none';
                renderBrushes();
            }}
        }});

        function createBrushCard(name, lightValue, darkValue, lightValueHtml, darkValueHtml, lightAlpha, darkAlpha) {{
            const card = document.createElement('div');
            card.className = 'brush-card';

            const nameEl = document.createElement('div');
            nameEl.className = 'brush-name';
            nameEl.textContent = name;

            const previewEl = document.createElement('div');
            previewEl.className = 'color-preview';

            // Light theme color item
            const lightItem = document.createElement('div');
            lightItem.className = 'color-item light';

            const lightValueText = document.createElement('div');
            lightValueText.className = 'color-value';
            const lightOpacity = Math.round(lightAlpha * 100);
            lightValueText.textContent = lightOpacity === 100 ? lightValue : `${{lightValue}} (${{lightOpacity}}%)`;

            const lightBox = document.createElement('div');
            lightBox.className = 'color-box';

            const lightOverlay = document.createElement('div');
            lightOverlay.className = 'color-overlay';
            lightOverlay.style.backgroundColor = lightValueHtml;

            lightBox.appendChild(lightOverlay);

            const lightLabel = document.createElement('div');
            lightLabel.className = 'color-label';
            lightLabel.textContent = 'Light';

            lightItem.appendChild(lightValueText);
            lightItem.appendChild(lightBox);
            lightItem.appendChild(lightLabel);

            // Dark theme color item
            const darkItem = document.createElement('div');
            darkItem.className = 'color-item dark';

            const darkValueText = document.createElement('div');
            darkValueText.className = 'color-value';
            const darkOpacity = Math.round(darkAlpha * 100);
            darkValueText.textContent = darkOpacity === 100 ? darkValue : `${{darkValue}} (${{darkOpacity}}%)`;

            const darkBox = document.createElement('div');
            darkBox.className = 'color-box';

            const darkOverlay = document.createElement('div');
            darkOverlay.className = 'color-overlay';
            darkOverlay.style.backgroundColor = darkValueHtml;

            darkBox.appendChild(darkOverlay);

            const darkLabel = document.createElement('div');
            darkLabel.className = 'color-label';
            darkLabel.textContent = 'Dark';

            darkItem.appendChild(darkValueText);
            darkItem.appendChild(darkBox);
            darkItem.appendChild(darkLabel);

            previewEl.appendChild(lightItem);
            previewEl.appendChild(darkItem);

            card.appendChild(nameEl);
            card.appendChild(previewEl);

            // クリックでクリップボードにコピー
            card.addEventListener('click', () => {{
                const copyDynamicResource = document.getElementById('copy-dynamic-resource').checked;
                const textToCopy = copyDynamicResource ? `{{DynamicResource ${{name}}}}` : name;
                navigator.clipboard.writeText(textToCopy).then(() => {{
                    showToast(`"${{textToCopy}}" Copied`);
                }}).catch(err => {{
                    console.error('Failed to copy:', err);
                }});
            }});

            return card;
        }}

        function showToast(message) {{
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');

            setTimeout(() => {{
                toast.classList.remove('show');
            }}, 2000);
        }}

        function renderBrushes(filterText = '') {{
            const container = document.getElementById('grid-container');
            container.innerHTML = '';

            let filteredBrushes = Object.entries(brushes).filter(([name, values]) => {{
                // 名前での検索
                if (name.toLowerCase().includes(filterText.toLowerCase())) {{
                    return true;
                }}

                // 透明度での検索（例: 100, >30, <50, >=20, <=80）
                const opacityMatch = filterText.match(/^([<>]=?|==)(\\d+)$/);
                if (opacityMatch) {{
                    const operator = opacityMatch[1];
                    const targetOpacity = parseInt(opacityMatch[2], 10);
                    const lightOpacity = Math.round(values.light_alpha * 100);
                    const darkOpacity = Math.round(values.dark_alpha * 100);

                    switch (operator) {{
                        case '>':
                            return lightOpacity > targetOpacity || darkOpacity > targetOpacity;
                        case '<':
                            return lightOpacity < targetOpacity || darkOpacity < targetOpacity;
                        case '>=':
                            return lightOpacity >= targetOpacity || darkOpacity >= targetOpacity;
                        case '<=':
                            return lightOpacity <= targetOpacity || darkOpacity <= targetOpacity;
                        case '==':
                            return lightOpacity === targetOpacity || darkOpacity === targetOpacity;
                    }}
                }}

                // 数値のみの場合は完全一致
                const numericMatch = filterText.match(/^(\\d+)$/);
                if (numericMatch) {{
                    const targetOpacity = parseInt(numericMatch[1], 10);
                    const lightOpacity = Math.round(values.light_alpha * 100);
                    const darkOpacity = Math.round(values.dark_alpha * 100);
                    return lightOpacity === targetOpacity || darkOpacity === targetOpacity;
                }}

                return false;
            }});

            // ソート処理
            if (currentSort === 'name') {{
                filteredBrushes.sort((a, b) => a[0].localeCompare(b[0]));
            }} else if (currentSort === 'color') {{
                filteredBrushes.sort((a, b) => {{
                    const brightnessA = a[1].light_brightness;
                    const brightnessB = b[1].light_brightness;
                    return brightnessB - brightnessA;
                }});
            }}

            if (filteredBrushes.length === 0) {{
                const noResults = document.createElement('div');
                noResults.className = 'no-results';
                noResults.textContent = 'No matching brushes found';
                container.appendChild(noResults);
                return;
            }}

            filteredBrushes.forEach(([name, values]) => {{
                const card = createBrushCard(
                    name,
                    values.light_value,
                    values.dark_value,
                    values.light_value_html,
                    values.dark_value_html,
                    values.light_alpha,
                    values.dark_alpha
                );
                container.appendChild(card);
            }});
        }}

        // ソートボタンのイベントリスナー
        document.querySelectorAll('.sort-btn').forEach(btn => {{
            btn.addEventListener('click', (e) => {{
                const sortType = e.target.dataset.sort;
                currentSort = sortType;

                // アクティブクラスの切り替え
                document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');

                // 再描画
                const searchText = document.getElementById('search-input').value;
                renderBrushes(searchText);
            }});
        }});

        // 初期表示
        renderBrushes();
    </script>
</body>
</html>'''

        # index.htmlに書き込み
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)




def main():
    """エントリーポイント"""
    gen = Generator()
    gen.run()


if __name__ == "__main__":
    main()
