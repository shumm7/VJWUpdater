import os
import tkinter
import tkinter.font
from utils.core import Core
from utils.wiki import Wiki

class Gui():
    root: tkinter.Tk
    font: tkinter.font
    font_big: tkinter.font
    font_bold: tkinter.font
    core: Core
    wiki: Wiki
    force: bool

    def __init__(self, wiki: Wiki) -> None:
        self.root = tkinter.Tk()
        self.root.title("VJW Updater")
        self.root.geometry("720x400")
        self.font = tkinter.font.Font(family="Meiryo UI")
        self.font_big = tkinter.font.Font(family="Meiryo UI", size=16)
        self.font_bold = tkinter.font.Font(family="Meiryo UI", weight=tkinter.font.BOLD)
        self.wiki = wiki
        self.force = tkinter.BooleanVar(value = False)

        self.core = Core(self.root, self.wiki)

        self.set_window()

    def set_window(self):
        lbl_00 = tkinter.Label(self.root, text = "行う操作を選択してください。")
        
        # tools
        frm_tools = tkinter.Frame(self.root)
        chk_tools = tkinter.Checkbutton(frm_tools, text="Force Checking", command=self.chk_forcemode, variable=self.force)
        chk_tools.pack(side=tkinter.LEFT, anchor=tkinter.N)
        frm_tools.pack()

        # title
        frm_title = tkinter.Frame(self.root)
        lbl_title = tkinter.Label(frm_title, text="行う操作を選択してください", font=self.font_big)
        lbl_title.pack(side=tkinter.TOP, anchor=tkinter.N)
        frm_title.pack()
        
        # buttonframe
        frm_btn = tkinter.Frame(self.root)

        #row1
        frm_row1 = tkinter.Frame(frm_btn)
        lbl_row1 = tkinter.Label(frm_row1, text='キャッシュ', font=self.font_bold)
        button_11 = tkinter.Button(frm_row1, text='バージョン確認', font=self.font, command=self.core.cache.version_check)
        button_12 = tkinter.Button(frm_row1, text='取得', font=self.font, command=self.core.cache.fetch)

        lbl_row1.pack()
        button_11.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_12.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        frm_row1.pack(side=tkinter.LEFT, anchor=tkinter.N, fill=tkinter.Y, expand=True, padx=5, pady=5, ipadx=5, ipady=5)

        #row2
        frm_row2 = tkinter.Frame(frm_btn)
        lbl_row2 = tkinter.Label(frm_row2, text='更新', font=self.font_bold)
        button_21 = tkinter.Button(frm_row2, text='プレイヤーカード', font=self.font, command=self.core.update.playercards)
        button_22 = tkinter.Button(frm_row2, text='スプレー', font=self.font, command=self.core.update.sprays)
        button_23 = tkinter.Button(frm_row2, text='ガンバディー', font=self.font, command=self.core.update.buddies)
        button_24 = tkinter.Button(frm_row2, text='ランク', font=self.font, command=self.core.update.competitivetiers)
        button_25 = tkinter.Button(frm_row2, text='エージェント', font=self.font, command=self.core.update.agents)
        button_26 = tkinter.Button(frm_row2, text='武器', font=self.font, command=self.core.update.weapons)
        button_27 = tkinter.Button(frm_row2, text='武器 (ビデオ)', font=self.font, command=self.core.update.skin_video)
        button_28 = tkinter.Button(frm_row2, text='レベルボーダー', font=self.font, command=self.core.update.levelborders)
        
        lbl_row2.pack()
        button_21.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_22.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_23.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_24.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_25.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_26.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_27.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_28.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        frm_row2.pack(side=tkinter.LEFT, anchor=tkinter.N, fill=tkinter.Y, expand=True, padx=5, pady=5)

        #row3
        frm_row3 = tkinter.Frame(frm_btn)
        lbl_row3 = tkinter.Label(frm_row3, text='Wiki構文', font=self.font_bold)
        button_31 = tkinter.Button(frm_row3, text='Infobox agent', font=self.font, command=self.core.wikitext.infobox_agents)
        button_32 = tkinter.Button(frm_row3, text='Contracts', font=self.font, command=self.core.wikitext.contracts)

        lbl_row3.pack()
        button_31.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_32.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        frm_row3.pack(side=tkinter.LEFT, anchor=tkinter.N, fill=tkinter.Y, expand=True, padx=5, pady=5, ipadx=5, ipady=5)

        #row4
        frm_row4 = tkinter.Frame(frm_btn)
        lbl_row4 = tkinter.Label(frm_row4, text='リスト', font=self.font_bold)
        button_41 = tkinter.Button(frm_row4, text='ガンバディー', font=self.font, command=self.core.list.gunbuddies)
        button_42 = tkinter.Button(frm_row4, text='スプレー', font=self.font, command=self.core.list.sprays)
        button_43 = tkinter.Button(frm_row4, text='プレイヤーカード', font=self.font, command=self.core.list.playercards)
        button_44 = tkinter.Button(frm_row4, text='タイトル', font=self.font, command=self.core.list.playertitles)
        button_45 = tkinter.Button(frm_row4, text='レベルボーダー', font=self.font, command=self.core.list.levelborders)
        
        lbl_row4.pack()
        button_41.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_42.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_43.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_44.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_45.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        frm_row4.pack(side=tkinter.LEFT, anchor=tkinter.N, fill=tkinter.Y, expand=True, padx=5, pady=5, ipadx=5, ipady=5)

        #row5
        frm_row5 = tkinter.Frame(frm_btn)
        lbl_row5 = tkinter.Label(frm_row5, text='e-Sports', font=self.font_bold)
        button_51 = tkinter.Button(frm_row5, text='Match', font=self.font, command=self.core.esports.match)
        button_52 = tkinter.Button(frm_row5, text='Match list', font=self.font, command=self.core.esports.matchlist)
        button_53 = tkinter.Button(frm_row5, text='Roster', font=self.font, command=self.core.esports.roster)
        
        lbl_row5.pack()
        button_51.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_52.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        button_53.pack(fill=tkinter.X, anchor=tkinter.N, padx=5, pady=5)
        frm_row5.pack(side=tkinter.LEFT, anchor=tkinter.N, fill=tkinter.Y, expand=True, padx=5, pady=5, ipadx=5, ipady=5)

        # buttonframe
        frm_btn.pack(fill=tkinter.BOTH, side=tkinter.LEFT, expand=True)

    
    def chk_forcemode(self):
        self.core.force = self.force.get()
