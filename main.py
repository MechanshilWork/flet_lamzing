import flet as ft
from updater import check_for_updates, perform_update

CURRENT_VERSION = "v1.0.0"
GITHUB_REPO = "MechanshilWork/flet_lamzing"

def main(page: ft.Page):
    print("App started!")
    page.title = "Self-Updating App"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    status_text = ft.Text(f"Current Version: {CURRENT_VERSION}", size=20, weight=ft.FontWeight.BOLD)
    update_button = ft.Button("Check for Updates", icon=ft.Icons.SYSTEM_UPDATE)
    progress_bar = ft.ProgressBar(visible=False, width=300, value=0)
    progress_text = ft.Text(visible=False)

    download_url_ref = [None]

    def on_update_clicked(e):
        update_button.disabled = True
        status_text.value = "Downloading and installing update..."
        progress_bar.visible = True
        progress_text.visible = True
        progress_bar.value = 0
        progress_text.value = "0%"
        page.update()

        def progress_callback(blocks, block_size, total_size):
            if total_size > 0:
                percent = (blocks * block_size) / total_size
                if percent > 1.0:
                    percent = 1.0
                progress_bar.value = percent
                progress_text.value = f"{int(percent * 100)}%"
                page.update()

        success = perform_update(download_url_ref[0], progress_callback)
        if success:
            status_text.value = "Update applied. Restart manually."
        else:
            status_text.value = "Update failed!"
        page.update()

    def on_check_updates(e):
        print("Button clicked!")
        update_button.disabled = True
        status_text.value = "Checking for updates..."
        page.update()

        latest_version, download_url = check_for_updates(CURRENT_VERSION, GITHUB_REPO)

        if latest_version and download_url:
            status_text.value = f"Update {latest_version} found!"
            download_url_ref[0] = download_url
            update_button.text = "Update"
            update_button.on_click = on_update_clicked
            update_button.disabled = False
        else:
            status_text.value = f"You are up to date! ({CURRENT_VERSION})"
            update_button.disabled = False

        page.update()

    update_button.on_click = on_check_updates

    page.add(
        ft.Icon(ft.Icons.ROCKET_LAUNCH, size=50, color=ft.Colors.BLUE_400),
        status_text,
        ft.Container(height=20),
        update_button,
        ft.Row([progress_bar, progress_text], alignment=ft.MainAxisAlignment.CENTER)
    )

if __name__ == '__main__':
    ft.run(main)