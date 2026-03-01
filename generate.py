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

    def construct_brushes(self):
        """light_xamlのcolor_brushesをループして、lightとdarkの値を持つ辞書を作成する"""
        for name, light_value in self.light_xaml.color_brushes.items():
            # dark_xamlから同名のキーの値を取得
            dark_value = self.dark_xaml.color_brushes.get(name)

            # HTML用のrgba形式に変換
            light_rgba, light_alpha = self.hex_to_rgba(light_value)
            dark_rgba, dark_alpha = self.hex_to_rgba(dark_value)

            self.brushes[name] = {
                "light_value": light_value,
                "dark_value": dark_value,
                "light_value_html": light_rgba,
                "dark_value_html": dark_rgba,
                "light_alpha": light_alpha,
                "dark_alpha": dark_alpha
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
            padding-top: 80px;
        }}

        header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 70px;
            background-color: #ffffff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            padding: 0 24px;
            z-index: 1000;
        }}

        h1 {{
            font-size: 20px;
            font-weight: 600;
            color: #333;
            margin-right: 24px;
        }}

        #search-input {{
            flex: 1;
            max-width: 400px;
            padding: 10px 16px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }}

        #search-input:focus {{
            border-color: #0078d4;
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

        .color-box {{
            flex: 1;
            height: 60px;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-family: monospace;
            color: #fff;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        }}

        .color-value {{
            font-size: 10px;
            margin-bottom: 4px;
        }}

        .color-label {{
            font-size: 11px;
            color: #666;
            margin-top: 4px;
            text-align: center;
        }}

        .no-results {{
            text-align: center;
            color: #666;
            padding: 40px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>WPF Theme Color Cheatsheet</h1>
        <input type="text" id="search-input" placeholder="ブラシ名で検索..." />
    </header>

    <main>
        <div id="grid-container"></div>
    </main>

    <script>
        const brushes = {brushes_json};

        function createBrushCard(name, lightValue, darkValue, lightValueHtml, darkValueHtml, lightAlpha, darkAlpha) {{
            const card = document.createElement('div');
            card.className = 'brush-card';

            const nameEl = document.createElement('div');
            nameEl.className = 'brush-name';
            nameEl.textContent = name;

            const previewEl = document.createElement('div');
            previewEl.className = 'color-preview';

            const lightBox = document.createElement('div');
            lightBox.className = 'color-box';
            lightBox.style.backgroundColor = lightValueHtml;

            const lightValueText = document.createElement('div');
            lightValueText.className = 'color-value';
            const lightOpacity = Math.round(lightAlpha * 100);
            lightValueText.textContent = lightOpacity === 100 ? lightValue : `${{lightValue}} (${{lightOpacity}}%)`;

            lightBox.appendChild(lightValueText);

            const darkBox = document.createElement('div');
            darkBox.className = 'color-box';
            darkBox.style.backgroundColor = darkValueHtml;

            const darkValueText = document.createElement('div');
            darkValueText.className = 'color-value';
            const darkOpacity = Math.round(darkAlpha * 100);
            darkValueText.textContent = darkOpacity === 100 ? darkValue : `${{darkValue}} (${{darkOpacity}}%)`;

            darkBox.appendChild(darkValueText);

            previewEl.appendChild(lightBox);
            previewEl.appendChild(darkBox);

            card.appendChild(nameEl);
            card.appendChild(previewEl);

            return card;
        }}

        function renderBrushes(filterText = '') {{
            const container = document.getElementById('grid-container');
            container.innerHTML = '';

            const filteredBrushes = Object.entries(brushes).filter(([name]) =>
                name.toLowerCase().includes(filterText.toLowerCase())
            );

            if (filteredBrushes.length === 0) {{
                const noResults = document.createElement('div');
                noResults.className = 'no-results';
                noResults.textContent = '該当するブラシが見つかりません';
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

        // 検索入力のイベントリスナー
        document.getElementById('search-input').addEventListener('input', (e) => {{
            renderBrushes(e.target.value);
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
