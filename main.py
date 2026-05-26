import flet as ft
from updater import check_for_updates, perform_update

# --- Configuration ---
CURRENT_VERSION = "v1.0.0"
GITHUB_REPO = "Mechanshil/flet_lamzing"

def main(page: ft.Page):
    page.title = "Self-Updating App"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    status_text = ft.Text(f"Current Version: {CURRENT_VERSION}", size=20, weight=ft.FontWeight.BOLD)
    update_button = ft.ElevatedButton("Check for Updates", icon=ft.icons.SYSTEM_UPDATE)
    progress_ring = ft.ProgressRing(visible=False, width=20, height=20)

    def on_check_updates(e):
        update_button.disabled = True
        progress_ring.visible = True
        status_text.value = "Checking for updates..."
        page.update()

        latest_version, download_url = check_for_updates(CURRENT_VERSION, GITHUB_REPO)

        if latest_version and download_url:
            status_text.value = f"Update {latest_version} found! Downloading and installing..."
            page.update()
            
            # Start the update process
            success = perform_update(download_url)
            if success:
                status_text.value = "Update applied (Dev Mode). Restart manually."
            else:
                status_text.value = "Update failed!"
        else:
            status_text.value = f"You are up to date! ({CURRENT_VERSION})"
        
        update_button.disabled = False
        progress_ring.visible = False
        page.update()

    update_button.on_click = on_check_updates

    page.add(
        ft.Icon(name=ft.icons.ROCKET_LAUNCH, size=50, color=ft.colors.BLUE_400),
        status_text,
        ft.Container(height=20), # Spacer
        ft.Row([update_button, progress_ring], alignment=ft.MainAxisAlignment.CENTER)
    )

if __name__ == '__main__':
    ft.app(target=main)
