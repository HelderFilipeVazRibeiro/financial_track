# run: flet run main.py -w
import flet as ft
import locale
import time

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")  # Local para o dólar
# locale.setlocale(locale.LC_ALL, "pt_PT.UTF-8") # Local para o euro

base_chart_style = {
    "expand": True,
    "tooltip_bgcolor": ft.colors.with_opacity(0.8, ft.colors.WHITE),
    "left_axis": ft.ChartAxis(labels_size=50),
    "bottom_axis": ft.ChartAxis(labels_interval=1, labels_size=40),
    "horizontal_grid_lines": ft.ChartGridLines(
        interval=10,
        color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE),
        width=1,
    ),
}


class BaseChart(ft.LineChart):
    def __init__(self, line_color: str) -> None:
        super().__init__(**base_chart_style)

        # create list to store coordinates
        self.points: list = []

        # set the min and max x axis
        self.min_x = (
            int(min(self.points, key=lambda x: x[0][0])) if self.points else None
        )

        self.max_x = (
            int(max(self.points, key=lambda x: x[0][0])) if self.points else None
        )

        # the main line to be display on the ui
        self.line = ft.LineChartData(
            color=line_color,  # red for out and green for in
            stroke_width=2,
            curved=True,
            stroke_cap_round=True,
            below_line_gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[
                    ft.colors.with_opacity(0.25, line_color),
                    "transparent",
                ],
            ),
        )

        self.line.data_points = self.points
        self.data_series = [self.line]

    # function that appends the data from the tracker to the charts
    def create_data_points(self, x, y) -> None:
        self.points.append(
            ft.LineChartDataPoint(
                x,
                y,
                selected_below_line=ft.ChartPointLine(
                    width=0.5, color="white54", dash_pattern=[2, 4]
                ),
                selected_point=ft.ChartCirclePoint(stroke_width=1),
            ),
        )

        self.update()


in_style = {
    "expand": 1,
    "bgcolor": "#17181d",
    "border_radius": 10,
    "padding": 30,
}


class GraphIn(ft.Container):
    def __init__(self) -> None:
        super().__init__(**in_style)
        self.chart = BaseChart(line_color="teal600")
        self.content = self.chart


out_style = {
    "expand": 1,
    "bgcolor": "#17181d",
    "border_radius": 10,
    "padding": 30,
}


class GraphOut(ft.Container):
    def __init__(self) -> None:
        super().__init__(**out_style)
        self.chart = BaseChart(line_color="red500")
        self.content = self.chart


tracker_style = {
    "main": {
        "expand": True,
        "bgcolor": "#17181d",
        "border_radius": 10,
    },
    "balance": {
        "size": 68,
        "weight": "bold",
        "color": "white",
    },
    "input": {  # style for input field
        "width": 220,
        "height": 40,
        "border_color": "white12",
        "cursor_height": 16,
        "cursor_color": "white12",
        "content_padding": 10,
        "text_align": "center",
        "color": "white",
    },
    "add": {  # style for add button
        "icon": ft.icons.ADD,
        "bgcolor": "#1f2128",
        "icon_size": 16,
        "icon_color": "teal600",
        "scale": ft.transform.Scale(0.8),
    },
    "subtract": {  # style for remove button
        "icon": ft.icons.REMOVE,
        "bgcolor": "#1f2128",
        "icon_size": 16,
        "icon_color": "red600",
        "scale": ft.transform.Scale(0.8),
    },
    "data_table": {  # style for datatables
        "columns": [  # column headers, in a bit
            ft.DataColumn(ft.Text("Timestamp", weight="w900")),
            ft.DataColumn(ft.Text("Amount", weight="w900"), numeric=True),
        ],
        "width": 380,
        "heading_row_height": 35,
        "data_row_max_height": 40,
    },
    "data_table_container": {  # for the container containing
        "expand": True,
        "width": 450,
        "padding": 10,
        "border_radius": ft.border_radius.only(top_left=10, top_right=10),
        "shadow": ft.BoxShadow(
            spread_radius=8,
            blur_radius=15,
            color=ft.colors.with_opacity(0.15, "black"),
            offset=ft.Offset(4, 4),
        ),
        "bgcolor": ft.colors.with_opacity(0.75, "#1f2128"),
    },
}


class Tracker(ft.Container):
    def __init__(self, _in: object, _out: object) -> None:
        super().__init__(**tracker_style.get("main"))
        self._in: object = _in
        self._out: object = _out

        self.counter = 0.0
        self.balance = ft.Text(
            locale.currency(self.counter, grouping=True),
            **tracker_style.get("balance")
        )

        self.input = ft.TextField(**tracker_style.get("input"))

        self.add = ft.IconButton(
            **tracker_style.get("add"),
            data=True,
            on_click=lambda e: self.update_balance(e),
        )

        self.subtract = ft.IconButton(
            **tracker_style.get("subtract"),
            data=False,
            on_click=lambda e: self.update_balance(e),
        )

        self.table = ft.DataTable(**tracker_style.get("data_table"))

        self.content = ft.Column(
            horizontal_alignment="center",
            controls=[
                ft.Divider(height=15, color="transparent"),
                ft.Text("Total Balance", size=16, weight="w900"),
                ft.Row(alignment="center", controls=[self.balance]),
                ft.Divider(height=15, color="transparent"),
                ft.Row(
                    alignment="center",
                    controls=[
                        self.subtract,
                        self.input,
                        self.add,
                    ],
                ),
                ft.Divider(height=25, color="transparent"),
                ft.Container(
                    **tracker_style.get("data_table_container"),
                    content=ft.Column(
                        expand=True,
                        scroll="hidden",
                        controls=[
                            self.table,
                        ],
                    ),
                ),
            ],
        )

        # for show purposes
        self.x = 0

    # first update datatables
    def update_data_table(self, amount: float, sign: bool) -> None:
        timestamp = int(time.time())
        data = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(timestamp)),
                ft.DataCell(
                    ft.Text(
                        locale.currency(amount, grouping=True),
                        color="teal" if sign else "red",
                    )
                ),
            ]
        )

        self.table.rows.append(data)
        self.table.update()

        return timestamp

    def update_balance(self, event) -> None:
        # check to see if input is not empty and value is digits
        if self.input.value != "" and self.input.value.isdigit():
            # get the input value and change it to float
            delta: float = float(self.input.value)
            # check which button was clicked - or +
            if event.control.data:
                self.counter += delta
                self.update_data_table(delta, sign=True)
                # to show the amounts on the charts
                # chart is the self.chart in the base class
                # create_data_points() is a function in the BaseChart class that creates coordinates. take 2 arguments x and y
                self._in.chart.create_data_points(
                    x=self.x,
                    y=delta,
                )
                self.x += 1

            else:
                self.counter -= delta
                self.update_data_table(delta, sign=False)
                # change _in to _out!!!!
                self._out.chart.create_data_points(
                    x=self.x,
                    y=delta,
                )
                self.x += 1

            # update UI
            self.balance.value = locale.currency(self.counter, grouping=True)
            self.balance.update()
            self.input.value = ""  # clear input field
            self.input.update()


def main(page: ft.Page) -> None:
    page.padding = 30
    page.bgcolor = "#1f2128"

    graph_in: ft.Container = GraphIn()
    graph_out: ft.Container = GraphOut()
    tracker: ft.Container = Tracker(_in=graph_in, _out=graph_out)

    page.add(
        ft.Row(
            expand=True,
            controls=[
                tracker,
                ft.Column(
                    expand=True,
                    controls=[graph_in, graph_out],
                ),
            ],
        ),
    )

    page.update()


if __name__ == "__main__":
    ft.app(target=main)
