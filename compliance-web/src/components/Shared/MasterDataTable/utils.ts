import dateUtils from "@/utils/dateUtils";
import { json2csv } from "json-2-csv";
import { MRT_TableInstance } from "material-react-table";
import { MRT_RowData } from "material-react-table";


interface ExportToCsvOptions<T extends MRT_RowData> {
  table: MRT_TableInstance<T>;
  downloadDate: string | null;
  filenamePrefix: string;
}

export async function exportToCsv<T extends MRT_RowData>({
  table,
  downloadDate,
  filenamePrefix,
}: ExportToCsvOptions<T>) {
  const columns = table
    .getVisibleFlatColumns()
    .map((p) => p.columnDef.id?.toString());

  const csvRows = table.getFilteredRowModel().flatRows.map((row) => {
    const csvRow: { [key: string]: unknown } = {};
    columns.forEach((column: string | undefined) => {
      if (column) {
        csvRow[column] = row.getValue(column);
      }
    });
    return csvRow;
  });

  const csv = await json2csv(csvRows, {
    emptyFieldValue: "",
    keys: columns as string[],
  });

  const url = window.URL.createObjectURL(new Blob([csv as never]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute(
    "download",
    `${filenamePrefix}-${dateUtils.formatDate(
      downloadDate ? downloadDate : new Date().toISOString()
    )}.csv`
  );
  document.body.appendChild(link);
  link.click();
}

