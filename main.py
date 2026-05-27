import flet as ft
from updater import check_for_updates, download_update, perform_install

CURRENT_VERSION = "v1.0.3"
GITHUB_REPO = "MechanshilWork/flet_lamzing"

def main(page: ft.Page):
    page.title = "Self-Updating App"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    status_text = ft.Text(f"Current Version: {CURRENT_VERSION}", size=20, weight=ft.FontWeight.BOLD)
    progress_bar = ft.ProgressBar(visible=False, width=300, value=0)
    progress_text = ft.Text(visible=False, size=12)
    download_url_ref = [None]

    def get_column():
        return page.controls[0]

    def set_button(new_button):
        col = get_column()
        col.controls[3] = new_button
        page.update()

    def on_install_clicked(e):
        status_text.value = "Installing update..."
        progress_bar.visible = False
        progress_text.visible = False
        set_button(ft.FilledButton("Installing...", icon=ft.Icons.SETTINGS, disabled=True))

        success = perform_install()
        if not success:
            status_text.value = "Install failed!"
            set_button(ft.FilledButton("Retry", icon=ft.Icons.REFRESH, on_click=on_install_clicked))

    def on_update_clicked(e):
        status_text.value = "Downloading update..."
        progress_bar.visible = True
        progress_bar.value = 0
        progress_text.visible = True
        progress_text.value = "0%"
        set_button(ft.FilledButton("Downloading...", icon=ft.Icons.DOWNLOAD, disabled=True))

        def progress_callback(blocks, block_size, total_size):
            if total_size > 0:
                percent = (blocks * block_size) / total_size
                if percent > 1.0:
                    percent = 1.0
                progress_bar.value = percent
                progress_text.value = f"{int(percent * 100)}%"
                page.update()

        success = download_update(download_url_ref[0], progress_callback)
        if success:
            status_text.value = "Download complete! Ready to install."
            progress_bar.value = 1.0
            progress_text.value = "100%"
            page.update()
            set_button(ft.FilledButton("Install Update", icon=ft.Icons.SYSTEM_UPDATE, on_click=on_install_clicked))
        else:
            status_text.value = "Download failed!"
            set_button(ft.FilledButton("Retry", icon=ft.Icons.REFRESH, on_click=on_update_clicked))

    def on_check_updates(e):
        set_button(ft.FilledButton("Checking...", icon=ft.Icons.SEARCH, disabled=True))
        status_text.value = "Checking for updates..."
        page.update()

        latest_version, download_url = check_for_updates(CURRENT_VERSION, GITHUB_REPO)

        if latest_version and download_url:
            status_text.value = f"Update {latest_version} found!"
            download_url_ref[0] = download_url
            set_button(ft.FilledButton("Update", icon=ft.Icons.DOWNLOAD, on_click=on_update_clicked))
        else:
            status_text.value = f"You are up to date! ({CURRENT_VERSION})"
            set_button(ft.FilledButton("Check for Updates", icon=ft.Icons.SYSTEM_UPDATE, on_click=on_check_updates))

    check_button = ft.FilledButton("Check for Updates", icon=ft.Icons.SYSTEM_UPDATE, on_click=on_check_updates)

    page.add(
        ft.Column(
            controls=[
                ft.Icon(ft.Icons.ROCKET_LAUNCH, size=50, color=ft.Colors.BLUE_400),
                status_text,
                ft.Container(height=20),
                check_button,
                ft.Row([progress_bar, ft.Container(width=10), progress_text], alignment=ft.MainAxisAlignment.CENTER)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

if __name__ == '__main__':
    ft.run(main)