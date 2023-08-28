import flet as ft
import datetime
import os
import zipfile
import subprocess
import shutil

from utils.tools.localize import Lang
from utils.tools.wiki import Wiki
from utils.tools.gui import Gui
from utils.tools.endpoint import Endpoint
from utils.tools.fetch import Fetch
from utils.tools.json import JSON
from utils.tools.api import API

class Misc():
    page: ft.Page
    wiki: Wiki
    gui: Gui
    content: ft.Container

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page) -> None:
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.store = Store(wiki, gui, page)

    
    def main(self):
        self.content = ft.Container(self.store.main(), expand=True)

        def on_clicked(e):
            i = e.control.selected_index
            contents = [
                self.store.main(),
            ]

            try:
                self.content.content = contents[i]
            except IndexError:
                pass
            self.gui.safe_update(self.content)
            

        return ft.Row(
            [
                ft.NavigationRail(
                    selected_index=0,
                    label_type=ft.NavigationRailLabelType.ALL,
                    min_width=100,
                    min_extended_width=400,
                    destinations=[
                        ft.NavigationRailDestination(
                            icon_content=ft.Icon(ft.icons.SHOPPING_BAG_OUTLINED),
                            selected_icon_content=ft.Icon(ft.icons.SHOPPING_BAG),
                            label=Lang.value("contents.misc.store.title"),
                        ),
                    ],
                    on_change=on_clicked
                ),
                ft.Card(
                    content=ft.Column([
                        ft.Container(
                            width=500,
                            padding=20,
                            content = self.content,
                        )],
                        horizontal_alignment=ft.MainAxisAlignment.START,
                        scroll=True
                    ),
                    expand=True
                )
            ]
        )

class Store():
    endpoint: Endpoint
    wiki: Wiki
    page: ft.Page
    gui: Gui
    storefront: dict = {}
    offer_display: ft.Column
    bundle_display: ft.Column
    accessory_display: ft.Column
    offer_remain: int = 0
    bundle_remain: int = 0
    accessory_remain: int = 0
    select: str

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.remain_display = ft.Text(value=self.date_format(0), style=ft.TextThemeStyle.BODY_MEDIUM)
        self.select = "offer"

        self.offer_display = ft.Column(controls=[], scroll=True)
        self.bundle_display = ft.Column(controls=[], scroll=True)
        self.accessory_display = ft.Column(controls=[], scroll=True)
        self.purchased_icon = ft.IconButton(icon=ft.icons.CHECK_CIRCLE, tooltip=Lang.value("contents.misc.store.own"), icon_color="green")

        self.animation = ft.AnimatedSwitcher(
            content=self.offer_display,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=500,
            reverse_duration=100,
            switch_in_curve=ft.AnimationCurve.EASE_IN,
            switch_out_curve=ft.AnimationCurve.EASE_IN,
        )

        try:
            self.endpoint = Endpoint()
            self.storefront = self.endpoint.fetch_storefront()
        except Exception as e:
            pass

        self.panel_placeholder()
            
        self.remain_display.value = self.date_format(0)
        self.gui.safe_update(self.remain_display)

    def main(self):
        # Reload Button
        def reload_clicked(e):
            try:
                self.endpoint = Endpoint()
                self.storefront = self.endpoint.fetch_storefront()
                self.entitlement = self.endpoint.fetch_entitlements()
            except :
                pass
            
            self.panel_offer()
            self.panel_bundle()
            self.panel_accessory()

            if self.select=="offer":
                self.remain_display.value = self.date_format(self.offer_remain)
                self.gui.safe_update(self.remain_display)
            elif self.select=="bundle":
                self.remain_display.value = self.date_format(self.bundle_remain)
                self.gui.safe_update(self.remain_display)
            elif self.select!="accessory":
                self.remain_display.value = self.date_format(self.accessory_remain)
                self.gui.safe_update(self.remain_display)

        self.reload_button = ft.IconButton(icon=ft.icons.REFRESH, on_click=reload_clicked, tooltip=Lang.value("contents.misc.store.reload"))

        # Animation Switcher
        def offer_button_clicked(e):
            if self.select!="offer":
                self.select="offer"
                self.animation.content = self.offer_display
                self.gui.safe_update(self.animation)
                self.remain_display.value = self.date_format(self.offer_remain)
                self.gui.safe_update(self.remain_display)
        def bundle_button_clicked(e):
            if self.select!="bundle":
                self.select="bundle"
                self.animation.content = self.bundle_display
                self.gui.safe_update(self.animation)
                self.remain_display.value = self.date_format(self.bundle_remain)
                self.gui.safe_update(self.remain_display)
        def accessory_button_clicked(e):
            if self.select!="accessory":
                self.select="accessory"
                self.animation.content = self.accessory_display
                self.gui.safe_update(self.animation)
                self.remain_display.value = self.date_format(self.accessory_remain)
                self.gui.safe_update(self.remain_display)

        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.misc.store.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.misc.store.description"), style=ft.TextThemeStyle.BODY_SMALL),
                ),
                ft.Divider(),
                
                ft.Column(
                    [
                        self.remain_display,
                        ft.Row(
                            [
                                ft.OutlinedButton(text=Lang.value("contents.misc.store.offer"), on_click=offer_button_clicked),
                                ft.OutlinedButton(text=Lang.value("contents.misc.store.featured_bundle"), on_click=bundle_button_clicked),
                                ft.OutlinedButton(text=Lang.value("contents.misc.store.accessory_store"), on_click=accessory_button_clicked),
                                self.reload_button
                            ]
                        ),
                        self.animation
                        
                    ],
                    scroll=True
                )
            ],
            scroll=True
        )
    
    def get_storefront(self) -> None:
        try:
            self.storefront = self.endpoint.fetch_storefront()
            self.entitlement = self.endpoint.fetch_entitlements()
        except Exception as e:
            self.gui.popup_error(Lang.value("contents.misc.store.failed"), str(e))
    
    def date_format(self, sec: int) -> str:
        td: datetime.timedelta = datetime.timedelta(seconds=sec)

        total_sec = td.total_seconds()
        day = td.days
        hour = total_sec // 3600
        minute = (total_sec - (hour * 3600)) // 60
        second = (total_sec - (hour * 3600)) - (minute * 60)

        return Lang.value("contents.misc.store.time").format(
            day=int(day),
            hour=int(hour) - (day * 24),
            minute=int(minute),
            second=int(second)
        )
    
    def panel_offer(self):
        offers: list = self.storefront.get("SkinsPanelLayout", {}).get("SingleItemStoreOffers", [])
        remain: int = self.storefront.get("SkinsPanelLayout", {}).get("SingleItemOffersRemainingDurationInSeconds", 0)

        self.offer_remain = remain
        self.offer_display.controls.clear()
        entitlement_list: list
        try:
            entitlement_list = API.entitlements_from_type_id(API.type_id_by_type("skins"), self.entitlement)
        except:
            entitlement_list = []

        for offer in offers:
            skin = API.skin_by_skinlevel_uuid(offer.get("OfferID", ""))

            name = skin.get("displayName", {}).get(Lang.value("common.localize"), "")
            image = skin.get("displayIcon", "/")
            price = offer.get("Cost", {}).get("85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741", 0)
            
            r = ft.Row([ft.Text(value=name, weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM)])
            if skin.get("uuid") in entitlement_list:
                r.controls.append(self.purchased_icon)
            self.offer_display.controls.append(
                ft.Column([
                    ft.Row(
                        [
                            ft.Image(src=image, width=200, height=100, fit=ft.ImageFit.CONTAIN),
                            ft.Column([r, ft.Text(value=Lang.value("common.price.valorant_point").format(price=price), style=ft.TextThemeStyle.BODY_SMALL)])
                        ]
                    ),
                    ft.Divider()
                ])
            )

        if len(self.offer_display.controls)<4:
            for i in range(4 - len(self.offer_display.controls)):
                self.offer_display.controls.append(
                    ft.Column([
                        ft.Row(
                            [
                                ft.Image(src="/", width=200, height=100, fit=ft.ImageFit.CONTAIN),
                                ft.Column([ft.Text(value="", weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM), ft.Text(value="", style=ft.TextThemeStyle.BODY_SMALL)])
                            ]
                        ),
                        ft.Divider()
                    ])
                )
        self.gui.safe_update(self.offer_display)

    def panel_bundle(self):
        bundles: list = self.storefront.get("FeaturedBundle", {}).get("Bundles", [])
        remain: int = self.storefront.get("FeaturedBundle", {}).get("BundleRemainingDurationInSeconds", 0)

        self.bundle_remain = remain
        self.bundle_display.controls.clear()

        for bundle in bundles:
            data = API.bundle_by_uuid(bundle.get("DataAssetID", ""))

            name = data.get("displayName", {}).get(Lang.value("common.localize"), "")
            image = data.get("displayIcon", "/")
            price = bundle.get("TotalDiscountedCost", {}).get("85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741", 0)
            base_price = bundle.get("TotalBaseCost", {}).get("85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741", 0)
            remain_each = bundle.get("DurationRemainingInSeconds", 0)

            self.bundle_display.controls.append(
                ft.Column([
                    ft.Row(
                        [
                            ft.Image(src=image, width=200, height=100, fit=ft.ImageFit.CONTAIN),
                            ft.Column([
                                ft.Text(value=name, weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM),
                                ft.Row([
                                    ft.Text(value=Lang.value("common.price.valorant_point").format(price=price), style=ft.TextThemeStyle.BODY_SMALL),
                                    ft.Container(padding=3),
                                    ft.Text(
                                        spans=[
                                            ft.TextSpan(Lang.value("common.price.valorant_point").format(price=base_price), ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, decoration_thickness=2))
                                        ],
                                        style=ft.TextThemeStyle.BODY_SMALL
                                    )
                                ]),
                                ft.Text(value=self.date_format(remain_each), style=ft.TextThemeStyle.BODY_SMALL),
                            ])
                        ]
                    ),
                    ft.Divider()
                ])
            )
        self.gui.safe_update(self.bundle_display)

    def panel_accessory(self):
        accessories: list = self.storefront.get("AccessoryStore", {}).get("AccessoryStoreOffers", [])
        remain: int = self.storefront.get("AccessoryStore", {}).get("AccessoryStoreRemainingDurationInSeconds", 0)

        self.accessory_remain = remain
        self.accessory_display.controls.clear()

        for accessory in accessories:
            itemtypeid = accessory.get("Offer", {}).get("Rewards", [])[0].get("ItemTypeID", "")
            itemtype = API.type_by_item_type_id(itemtypeid)
            itemid = accessory.get("Offer", {}).get("Rewards", [])[0].get("ItemID", "")
            

            if itemtype=="playercards":
                skin = API.playercard_by_uuid(itemid)
            elif itemtype=="sprays":
                skin = API.spray_by_uuid(itemid)
            elif itemtype=="buddies":
                skin = API.buddy_by_charmlevel_uuid(itemid)
            else:
                skin = {}
            name = skin.get("displayName", {}).get(Lang.value("common.localize"), "")
            image = skin.get("displayIcon", "/")
            price = accessory.get("Offer", {}).get("Cost", {}).get("85ca954a-41f2-ce94-9b45-8ca3dd39a00d", 0)

            entitlement_list: list
            try:
                entitlement_list = API.entitlements_from_type_id(itemtypeid, self.entitlement)
            except:
                entitlement_list = []

            r = ft.Row([ft.Text(value=name, weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM)])
            if itemid in entitlement_list:
                r.controls.append(self.purchased_icon)
            self.accessory_display.controls.append(
                ft.Column([
                    ft.Row(
                        [
                            ft.Image(src=image, width=200, height=100, fit=ft.ImageFit.CONTAIN),
                            ft.Column([r, ft.Text(value=Lang.value("common.price.kingdom_credit").format(price=price), style=ft.TextThemeStyle.BODY_SMALL)])
                        ]
                    ),
                    ft.Divider()
                ])
            )

        self.gui.safe_update(self.accessory_display)
    
    def panel_placeholder(self):
        for i in range(4):
            self.offer_display.controls.append(
                ft.Column([
                    ft.Row(
                        [
                            ft.Image(src="/", width=200, height=100, fit=ft.ImageFit.CONTAIN),
                            ft.Column([ft.Text(value="", weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM), ft.Text(value="", style=ft.TextThemeStyle.BODY_SMALL)])
                        ]
                    ),
                    ft.Divider()
                ])
            )
            self.bundle_display.controls.append(
                ft.Column([
                    ft.Row(
                        [
                            ft.Image(src="/", width=200, height=100, fit=ft.ImageFit.CONTAIN),
                            ft.Column([ft.Text(value="", weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM), ft.Text(value="", style=ft.TextThemeStyle.BODY_SMALL)])
                        ]
                    ),
                    ft.Divider()
                ])
            )
            self.accessory_display.controls.append(
                ft.Column([
                    ft.Row(
                        [
                            ft.Image(src="/", width=200, height=100, fit=ft.ImageFit.CONTAIN),
                            ft.Column([ft.Text(value="", weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM), ft.Text(value="", style=ft.TextThemeStyle.BODY_SMALL)])
                        ]
                    ),
                    ft.Divider()
                ])
            )

