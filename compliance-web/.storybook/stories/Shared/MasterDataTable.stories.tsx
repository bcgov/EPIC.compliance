import type { Meta, StoryObj } from "@storybook/react";
import React, { useState, useMemo } from "react";
import { Box, Typography, Chip, IconButton, Tooltip } from "@mui/material";
import {
  MRT_ColumnDef,
  MRT_SortingState,
  MRT_ColumnFiltersState,
} from "material-react-table";
import {
  EditRounded,
  DeleteRounded,
  VisibilityRounded,
} from "@mui/icons-material";
import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";

// Sample data types
interface Person {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  age: number;
  city: string;
  state: string;
  status: "active" | "inactive" | "pending";
  joinDate: string;
  salary: number;
  department: string;
}

// Sample data
const sampleData: Person[] = [
  {
    id: 1,
    firstName: "John",
    lastName: "Doe",
    email: "john.doe@example.com",
    age: 28,
    city: "Vancouver",
    state: "BC",
    status: "active",
    joinDate: "2023-01-15",
    salary: 75000,
    department: "Engineering",
  },
  {
    id: 2,
    firstName: "Jane",
    lastName: "Smith",
    email: "jane.smith@example.com",
    age: 32,
    city: "Toronto",
    state: "ON",
    status: "active",
    joinDate: "2022-11-20",
    salary: 82000,
    department: "Marketing",
  },
  {
    id: 3,
    firstName: "Bob",
    lastName: "Johnson",
    email: "bob.johnson@example.com",
    age: 45,
    city: "Montreal",
    state: "QC",
    status: "inactive",
    joinDate: "2021-03-10",
    salary: 95000,
    department: "Sales",
  },
  {
    id: 4,
    firstName: "Alice",
    lastName: "Brown",
    email: "alice.brown@example.com",
    age: 29,
    city: "Calgary",
    state: "AB",
    status: "pending",
    joinDate: "2024-01-05",
    salary: 68000,
    department: "HR",
  },
  {
    id: 5,
    firstName: "Charlie",
    lastName: "Wilson",
    email: "charlie.wilson@example.com",
    age: 38,
    city: "Ottawa",
    state: "ON",
    status: "active",
    joinDate: "2023-06-15",
    salary: 78000,
    department: "Engineering",
  },
  {
    id: 6,
    firstName: "Diana",
    lastName: "Davis",
    email: "diana.davis@example.com",
    age: 31,
    city: "Victoria",
    state: "BC",
    status: "active",
    joinDate: "2022-09-12",
    salary: 71000,
    department: "Finance",
  },
  {
    id: 7,
    firstName: "Eve",
    lastName: "Miller",
    email: "eve.miller@example.com",
    age: 27,
    city: "Halifax",
    state: "NS",
    status: "inactive",
    joinDate: "2023-04-20",
    salary: 65000,
    department: "Marketing",
  },
  {
    id: 8,
    firstName: "Frank",
    lastName: "Garcia",
    email: "frank.garcia@example.com",
    age: 42,
    city: "Winnipeg",
    state: "MB",
    status: "active",
    joinDate: "2021-12-01",
    salary: 88000,
    department: "Sales",
  },
];

// Status chip component
const StatusChip = ({ status }: { status: string }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "success";
      case "inactive":
        return "error";
      case "pending":
        return "warning";
      default:
        return "default";
    }
  };

  return (
    <Chip
      label={status.charAt(0).toUpperCase() + status.slice(1)}
      color={getStatusColor(status) as any}
      size="small"
    />
  );
};

// Demo component showing different table configurations
const MasterDataTableDemo = () => {
  const [data, setData] = useState<Person[]>(sampleData);

  // Column definitions
  const columns: MRT_ColumnDef<Person>[] = useMemo(
    () => [
      {
        accessorKey: "id",
        header: "ID",
        size: 60,
        enableSorting: false,
        enableColumnFilter: false,
      },
      {
        accessorKey: "firstName",
        header: "First Name",
        size: 120,
        filterSelectOptions: getSelectFilterOptions(data, "firstName"),
        filterVariant: "multi-select",
      },
      {
        accessorKey: "lastName",
        header: "Last Name",
        size: 120,
        filterSelectOptions: getSelectFilterOptions(data, "lastName"),
        filterVariant: "multi-select",
      },
      {
        accessorKey: "email",
        header: "Email",
        size: 200,
        enableColumnFilter: false,
      },
      {
        accessorKey: "age",
        header: "Age",
        size: 80,
        enableColumnFilter: false,
      },
      {
        accessorKey: "city",
        header: "City",
        size: 120,
        filterSelectOptions: getSelectFilterOptions(data, "city"),
        filterVariant: "multi-select",
      },
      {
        accessorKey: "state",
        header: "State",
        size: 80,
        filterSelectOptions: getSelectFilterOptions(data, "state"),
        filterVariant: "multi-select",
      },
      {
        accessorKey: "status",
        header: "Status",
        size: 100,
        Cell: ({ cell }) => <StatusChip status={cell.getValue<string>()} />,
        filterSelectOptions: getSelectFilterOptions(data, "status"),
        filterVariant: "multi-select",
      },
      {
        accessorKey: "joinDate",
        header: "Join Date",
        size: 120,
        filterVariant: "date",
      },
      {
        accessorKey: "salary",
        header: "Salary",
        size: 100,
        Cell: ({ cell }) => `$${cell.getValue<number>().toLocaleString()}`,
        enableColumnFilter: false,
      },
      {
        accessorKey: "department",
        header: "Department",
        size: 120,
        filterSelectOptions: getSelectFilterOptions(data, "department"),
        filterVariant: "multi-select",
      },
    ],
    [data]
  );

  // Helper function to get filter options
  function getSelectFilterOptions<T>(
    data: T[],
    key: keyof T,
    formatLabel: (value: unknown) => string = (value) => String(value),
    formatValue: (value: unknown) => unknown = (value) => String(value)
  ) {
    const optionsMap = new Map();

    data.forEach((dataObject) => {
      if (
        !dataObject ||
        dataObject[key] === undefined ||
        dataObject[key] === null
      ) {
        optionsMap.set("", "(Blanks)");
        return;
      }
      optionsMap.set(
        formatValue(dataObject[key]),
        formatLabel(dataObject[key])
      );
    });

    const optionsArray = Array.from(optionsMap.entries()).map(
      ([key, value]) => ({
        text: value,
        value: key,
      })
    );

    optionsArray.sort((a, b) => {
      if (a.value === "") return -1;
      if (b.value === "") return 1;
      return a.value < b.value ? -1 : 1;
    });

    return optionsArray;
  }

  const handleAddRecord = () => {
    const newRecord: Person = {
      id: Math.max(...data.map((p) => p.id)) + 1,
      firstName: "New",
      lastName: "User",
      email: "new.user@example.com",
      age: 25,
      city: "Vancouver",
      state: "BC",
      status: "pending",
      joinDate: new Date().toISOString().split("T")[0],
      salary: 50000,
      department: "Engineering",
    };
    setData([...data, newRecord]);
  };

  const handleEditRecord = (row: any) => {
    console.log("Edit record:", row.original);
  };

  const handleDeleteRecord = (row: any) => {
    setData(data.filter((p) => p.id !== row.original.id));
  };

  const handleViewRecord = (row: any) => {
    console.log("View record:", row.original);
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Master Data Table Examples
      </Typography>
      <Typography variant="body1" paragraph>
        This comprehensive example demonstrates the MasterDataTable component
        with various features including filtering, sorting, pagination, and
        actions.
      </Typography>

      <MasterDataTable
        columns={columns}
        data={data}
        enableExport={true}
        tableName="employees"
        titleToolbarProps={{
          tableTitle: "Employee Management",
          tableAddRecordButtonText: "Add Employee",
          tableAddRecordButtonVisibility: true,
          tableAddRecordFunction: handleAddRecord,
        }}
        renderRowActions={({ row }) => (
          <Box sx={{ display: "flex", gap: "0.5rem" }}>
            <Tooltip title="View">
              <IconButton size="small" onClick={() => handleViewRecord(row)}>
                <VisibilityRounded />
              </IconButton>
            </Tooltip>
            <Tooltip title="Edit">
              <IconButton size="small" onClick={() => handleEditRecord(row)}>
                <EditRounded />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete">
              <IconButton
                size="small"
                onClick={() => handleDeleteRecord(row)}
                color="error"
              >
                <DeleteRounded />
              </IconButton>
            </Tooltip>
          </Box>
        )}
        enableRowSelection={true}
        enableMultiRowSelection={true}
        enableSelectAll={true}
        enableHiding={false}
        enableColumnResizing={true}
        enableStickyHeader={true}
        enableDensityToggle={false}
        enableFullScreenToggle={false}
        enableSorting={true}
        enableFilters={true}
        enableColumnActions={false}
        enablePinning={true}
        positionActionsColumn="last"
        muiTableBodyRowProps={({ row }) => ({
          onClick: () => console.log("Row clicked:", row.original),
          sx: {
            cursor: "pointer",
            "&:hover": {
              backgroundColor: "rgba(0, 0, 0, 0.04)",
            },
          },
        })}
      />
    </Box>
  );
};

// Remote data demo
const RemoteDataDemoComponent = () => {
  const [data, setData] = useState<Person[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });
  const [sorting, setSorting] = useState<MRT_SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<MRT_ColumnFiltersState>(
    []
  );
  const [globalFilter, setGlobalFilter] = useState("");
  const [rowCount, setRowCount] = useState(0);

  // Simulate API call
  const fetchData = async () => {
    setLoading(true);
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const start = pagination.pageIndex * pagination.pageSize;
    const end = start + pagination.pageSize;
    const filteredData = sampleData.slice(start, end);

    setData(filteredData);
    setRowCount(sampleData.length);
    setLoading(false);
  };

  React.useEffect(() => {
    fetchData();
  }, [pagination, sorting, columnFilters, globalFilter]);

  const columns: MRT_ColumnDef<Person>[] = useMemo(
    () => [
      {
        accessorKey: "id",
        header: "ID",
        size: 60,
      },
      {
        accessorKey: "firstName",
        header: "First Name",
        size: 120,
      },
      {
        accessorKey: "lastName",
        header: "Last Name",
        size: 120,
      },
      {
        accessorKey: "email",
        header: "Email",
        size: 200,
      },
      {
        accessorKey: "department",
        header: "Department",
        size: 120,
      },
    ],
    []
  );

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Remote Data Table
      </Typography>
      <Typography variant="body1" paragraph>
        This example demonstrates the table with remote data loading,
        pagination, and filtering.
      </Typography>

      <MasterDataTable
        columns={columns}
        data={data}
        state={{
          isLoading: loading,
          pagination,
          sorting,
          columnFilters,
          globalFilter,
        }}
        enableExport={true}
        tableName="remote-employees"
        titleToolbarProps={{
          tableTitle: "Remote Data Table",
          tableAddRecordButtonText: "Add Record",
          tableAddRecordButtonVisibility: true,
          tableAddRecordFunction: () => console.log("Add record"),
        }}
        remoteDataConfig={{
          enableRemoteData: true,
          rowCount,
          manualPagination: true,
          manualSorting: true,
          manualFiltering: true,
          onPaginationChange: setPagination,
          onSortingChange: setSorting,
          onColumnFiltersChange: setColumnFilters,
          onGlobalFilterChange: setGlobalFilter,
        }}
        enableRowSelection={false}
        enableHiding={false}
        enableColumnResizing={true}
        enableStickyHeader={true}
        enableDensityToggle={false}
        enableFullScreenToggle={false}
        enableSorting={true}
        enableFilters={true}
        enableColumnActions={false}
        enablePinning={true}
        positionActionsColumn="last"
      />
    </Box>
  );
};

const meta: Meta<typeof MasterDataTable> = {
  title: "Shared/MasterDataTable",
  component: MasterDataTable,
  parameters: {
    layout: "fullscreen",
  },
  decorators: [
    (Story) => (
      <div style={{ width: "100%", height: "100vh" }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof MasterDataTable>;

export const BasicTable: Story = {
  render: () => {
    const [data] = useState<Person[]>(sampleData.slice(0, 5));

    const columns: MRT_ColumnDef<Person>[] = useMemo(
      () => [
        {
          accessorKey: "firstName",
          header: "First Name",
          size: 120,
        },
        {
          accessorKey: "lastName",
          header: "Last Name",
          size: 120,
        },
        {
          accessorKey: "email",
          header: "Email",
          size: 200,
        },
        {
          accessorKey: "department",
          header: "Department",
          size: 120,
        },
      ],
      []
    );

    return (
      <Box sx={{ padding: "20px" }}>
        <MasterDataTable
          columns={columns}
          data={data}
          enableExport={true}
          tableName="basic-employees"
          titleToolbarProps={{
            tableTitle: "Basic Employee Table",
            tableAddRecordButtonText: "Add Employee",
            tableAddRecordButtonVisibility: true,
            tableAddRecordFunction: () => console.log("Add employee"),
          }}
        />
      </Box>
    );
  },
};

export const TableWithFilters: Story = {
  render: () => {
    const [data] = useState<Person[]>(sampleData);

    function getSelectFilterOptions<T>(
      data: T[],
      key: keyof T,
      formatLabel: (value: unknown) => string = (value) => String(value),
      formatValue: (value: unknown) => unknown = (value) => String(value)
    ) {
      const optionsMap = new Map();

      data.forEach((dataObject) => {
        if (
          !dataObject ||
          dataObject[key] === undefined ||
          dataObject[key] === null
        ) {
          optionsMap.set("", "(Blanks)");
          return;
        }
        optionsMap.set(
          formatValue(dataObject[key]),
          formatLabel(dataObject[key])
        );
      });

      const optionsArray = Array.from(optionsMap.entries()).map(
        ([key, value]) => ({
          text: value,
          value: key,
        })
      );

      optionsArray.sort((a, b) => {
        if (a.value === "") return -1;
        if (b.value === "") return 1;
        return a.value < b.value ? -1 : 1;
      });

      return optionsArray;
    }

    const columns: MRT_ColumnDef<Person>[] = useMemo(
      () => [
        {
          accessorKey: "firstName",
          header: "First Name",
          size: 120,
          filterSelectOptions: getSelectFilterOptions(data, "firstName"),
          filterVariant: "multi-select",
        },
        {
          accessorKey: "lastName",
          header: "Last Name",
          size: 120,
          filterSelectOptions: getSelectFilterOptions(data, "lastName"),
          filterVariant: "multi-select",
        },
        {
          accessorKey: "status",
          header: "Status",
          size: 100,
          Cell: ({ cell }) => <StatusChip status={cell.getValue<string>()} />,
          filterSelectOptions: getSelectFilterOptions(data, "status"),
          filterVariant: "multi-select",
        },
        {
          accessorKey: "joinDate",
          header: "Join Date",
          size: 120,
          filterVariant: "date",
        },
        {
          accessorKey: "department",
          header: "Department",
          size: 120,
          filterSelectOptions: getSelectFilterOptions(data, "department"),
          filterVariant: "multi-select",
        },
      ],
      [data]
    );

    return (
      <Box sx={{ padding: "20px" }}>
        <MasterDataTable
          columns={columns}
          data={data}
          enableExport={true}
          tableName="filtered-employees"
          titleToolbarProps={{
            tableTitle: "Filtered Employee Table",
            tableAddRecordButtonText: "Add Employee",
            tableAddRecordButtonVisibility: true,
            tableAddRecordFunction: () => console.log("Add employee"),
          }}
        />
      </Box>
    );
  },
};

export const RemoteDataDemo: Story = {
  render: () => <RemoteDataDemoComponent />,
};

export const InteractiveDemo: Story = {
  render: () => <MasterDataTableDemo />,
};

export const StackedTables: Story = {
  render: () => {
    const [data] = useState<Person[]>(sampleData);

    const columns: MRT_ColumnDef<Person>[] = useMemo(
      () => [
        {
          accessorKey: "firstName",
          header: "First Name",
          size: 120,
        },
        {
          accessorKey: "lastName",
          header: "Last Name",
          size: 120,
        },
        {
          accessorKey: "email",
          header: "Email",
          size: 200,
        },
        {
          accessorKey: "department",
          header: "Department",
          size: 120,
        },
      ],
      []
    );

    return (
      <Box sx={{ padding: "20px" }}>
        <Typography variant="h6" gutterBottom>
          Stacked Tables Example
        </Typography>
        <Typography variant="body1" paragraph>
          This example shows how tables look when stacked
          (isStackedTables=true).
        </Typography>

        <MasterDataTable
          columns={columns}
          data={data}
          isStackedTables={true}
          enableExport={true}
          tableName="stacked-employees"
          titleToolbarProps={{
            tableTitle: "Stacked Table 1",
            tableAddRecordButtonText: "Add Employee",
            tableAddRecordButtonVisibility: true,
            tableAddRecordFunction: () => console.log("Add employee"),
          }}
        />

        <Box sx={{ mt: 2 }}>
          <MasterDataTable
            columns={columns}
            data={data.slice(0, 3)}
            isStackedTables={true}
            enableExport={true}
            tableName="stacked-employees-2"
            titleToolbarProps={{
              tableTitle: "Stacked Table 2",
              tableAddRecordButtonText: "Add Employee",
              tableAddRecordButtonVisibility: true,
              tableAddRecordFunction: () => console.log("Add employee"),
            }}
          />
        </Box>
      </Box>
    );
  },
};
