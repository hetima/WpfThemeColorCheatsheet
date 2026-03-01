import xml.etree.ElementTree as ET
import re


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

    def construct_brushes(self):
        """light_xamlのcolor_brushesをループして、lightとdarkの値を持つ辞書を作成する"""
        for name, light_value in self.light_xaml.color_brushes.items():
            # dark_xamlから同名のキーの値を取得
            dark_value = self.dark_xaml.color_brushes.get(name)
            self.brushes[name] = {
                "light_value": light_value,
                "dark_value": dark_value
            }

    def run(self):
        """メイン処理を実行"""
        self.construct_brushes()




def main():
    """エントリーポイント"""
    gen = Generator()
    gen.run()


if __name__ == "__main__":
    main()
