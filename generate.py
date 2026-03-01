



class Xaml:
    def __init__(self, path: str):
        pass



class Generator:
    """main class"""

    def __init__(self):
        self.light_xaml = Xaml("light.xaml")
        self.dark_xaml = Xaml("dark.xaml")


    def run(self):
        """メイン処理を実行"""
        pass




def main():
    """エントリーポイント"""
    gen = Generator()
    gen.run()


if __name__ == "__main__":
    main()
