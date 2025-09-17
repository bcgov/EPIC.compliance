import type { Meta, StoryObj } from "@storybook/react";
import { useState, useCallback } from "react";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { ThemeProvider } from "@mui/material/styles";
import { createAppTheme } from "epic.theme";
import FilterSelect from "../../../src/components/Shared/FilterSelect/FilterSelect";
import TableFilter from "../../../src/components/Shared/FilterSelect/TableFilter";
import ExternalTableFilter from "../../../src/components/Shared/FilterSelect/ExternalTableFilter";
import DateFilter from "../../../src/components/Shared/FilterSelect/DateFilter";
import { OptionType } from "../../../src/components/Shared/FilterSelect/type";

// Mock data for stories
const mockOptions: OptionType[] = [
  { label: "Option 1", value: "option1" },
  { label: "Option 2", value: "option2" },
  { label: "Option 3", value: "option3" },
  { label: "Very Long Option Name That Should Wrap", value: "long-option" },
  { label: "Another Option", value: "another" },
  { label: "Final Option", value: "final" },
];

// Create a more complete mock for Material React Table types
const createMockTableColumn = (initialValue: any = []) =>
  ({
    id: "mock-column",
    columnDef: {
      filterSelectOptions: [
        "Active",
        "Inactive",
        "Pending",
        "Completed",
        "Draft",
        { text: "Custom Option", value: "custom" },
      ],
    },
    getFilterValue: () => initialValue,
    setFilterValue: (value: any) => console.log("Filter value set:", value),
  }) as any;

const createMockHeader = (column: any) => ({ column }) as any;

const meta: Meta<typeof FilterSelect> = {
  title: "Shared/Filters",
  component: FilterSelect,
  parameters: {
    layout: "centered",
    docs: {
      description: {
        component:
          "A comprehensive collection of filter select components including FilterSelect, TableFilter, ExternalTableFilter, and DateFilter.",
      },
    },
  },
  decorators: [
    (Story) => (
      <ThemeProvider theme={createAppTheme()}>
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <div style={{ minWidth: "300px", padding: "20px" }}>
            <Story />
          </div>
        </LocalizationProvider>
      </ThemeProvider>
    ),
  ],
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof meta>;

// FilterSelect Stories
const FilterSelectWrapper = (args: any) => {
  const [value, setValue] = useState(args.value || (args.isMulti ? [] : ""));

  const handleFilterApplied = useCallback(
    (selectedOptions: string[] | string) => {
      setValue(selectedOptions);
      args.filterAppliedCallback?.(selectedOptions);
    },
    [args]
  );

  const handleFilterCleared = useCallback(
    (value: [] | string) => {
      setValue(value);
      args.filterClearedCallback?.(value);
    },
    [args]
  );

  return (
    <FilterSelect
      {...args}
      value={value}
      filterAppliedCallback={handleFilterApplied}
      filterClearedCallback={handleFilterCleared}
    />
  );
};

export const BasicMultiSelect: Story = {
  render: FilterSelectWrapper,
  args: {
    options: mockOptions,
    placeholder: "Select multiple options",
    variant: "inline",
    isMulti: true,
  },
};

export const InlineVariant: Story = {
  render: FilterSelectWrapper,
  args: {
    options: mockOptions,
    placeholder: "Inline filter",
    variant: "inline",
    isMulti: true,
  },
};

export const BarVariant: Story = {
  render: FilterSelectWrapper,
  args: {
    options: mockOptions,
    placeholder: "Bar filter",
    variant: "bar",
    isMulti: true,
  },
};

export const DisabledState: Story = {
  render: FilterSelectWrapper,
  args: {
    options: mockOptions,
    placeholder: "Disabled filter",
    variant: "inline",
    isMulti: true,
    isDisabled: true,
  },
};

export const NonSearchable: Story = {
  render: FilterSelectWrapper,
  args: {
    options: mockOptions,
    placeholder: "Non-searchable",
    variant: "inline",
    isMulti: true,
    isSearchable: false,
  },
};

// TableFilter Stories
const TableFilterWrapper = (args: any) => {
  const [filterValue, setFilterValue] = useState(args.defaultValue || []);

  const mockColumn = {
    ...createMockTableColumn(filterValue),
    getFilterValue: () => filterValue,
    setFilterValue: (value: any) => {
      setFilterValue(value);
      console.log("Table filter value set:", value);
    },
  };

  const mockHeaderWithState = createMockHeader(mockColumn);

  return (
    <TableFilter {...args} header={mockHeaderWithState} column={mockColumn} />
  );
};

export const TableFilterSingle: Story = {
  render: TableFilterWrapper,
  args: {
    placeholder: "Table filter (single)",
    variant: "inline",
    isMulti: false,
  },
  parameters: {
    docs: {
      description: {
        story:
          "TableFilter component for use with Material React Table columns.",
      },
    },
  },
};

export const TableFilterMultiple: Story = {
  render: TableFilterWrapper,
  args: {
    placeholder: "Table filter (multi)",
    variant: "inline",
    isMulti: true,
  },
};

export const TableFilterWithInitialValue: Story = {
  render: (args: any) => {
    const [filterValue, setFilterValue] = useState(["Active", "Pending"]);

    const mockColumn = {
      ...createMockTableColumn(filterValue),
      getFilterValue: () => filterValue,
      setFilterValue: (value: any) => {
        setFilterValue(value);
        console.log("Table filter value set:", value);
      },
    };

    const mockHeaderWithState = createMockHeader(mockColumn);

    return (
      <TableFilter {...args} header={mockHeaderWithState} column={mockColumn} />
    );
  },
  args: {
    placeholder: "With initial value",
    variant: "inline",
    isMulti: true,
  },
};

// ExternalTableFilter Stories
const ExternalTableFilterWrapper = (args: any) => {
  const [filters, setFilters] = useState<Record<string, string[] | string>>(
    () => {
      // Initialize with some default values to show the count functionality
      if (args.filterId === "categories") {
        return { [args.filterId]: ["Category A", "Category B"] };
      }
      if (args.filterId === "types") {
        return { [args.filterId]: ["Type 1", "Type 3"] };
      }
      if (args.filterId === "priority") {
        return { [args.filterId]: ["High", "Medium"] };
      }
      return {};
    }
  );

  const handleFilterChange = useCallback(
    (filterId: string, value: string[] | string) => {
      setFilters((prev) => ({ ...prev, [filterId]: value }));
      console.log("External filter changed:", { filterId, value });
    },
    []
  );

  return (
    <div>
      <ExternalTableFilter
        {...args}
        onFilterChange={handleFilterChange}
        currentValue={filters[args.filterId]}
      />
      <div style={{ marginTop: "16px", fontSize: "12px", color: "#666" }}>
        Current filters: {JSON.stringify(filters)}
      </div>
    </div>
  );
};

export const ExternalFilterMultiple: Story = {
  render: ExternalTableFilterWrapper as any,
  args: {
    filterId: "categories",
    filterOptions: [
      "Category A",
      "Category B",
      "Category C",
      { text: "Custom Category", value: "custom-cat" },
    ],
    placeholder: "Categories",
    variant: "inline-standalone",
    isMulti: true,
  } as any,
  parameters: {
    docs: {
      description: {
        story:
          "ExternalTableFilter component for use external to Material React Table columns.",
      },
    },
  },
};

export const ExternalFilterBar: Story = {
  render: ExternalTableFilterWrapper as any,
  args: {
    filterId: "types",
    filterOptions: ["Type 1", "Type 2", "Type 3", "Type 4"],
    placeholder: "Types",
    variant: "bar",
    isMulti: true,
  } as any,
};

// DateFilter Stories
const DateFilterWrapper = (args: any) => {
  const [filterValue, setFilterValue] = useState("");

  const mockColumn = {
    id: "date-column",
    getFilterValue: () => filterValue,
    setFilterValue: (value: string) => {
      setFilterValue(value);
      console.log("Date filter value set:", value);
    },
  } as any;

  const mockHeaderWithState = createMockHeader(mockColumn);

  return (
    <DateFilter {...args} header={mockHeaderWithState} column={mockColumn} />
  );
};

export const BasicDateFilter: Story = {
  render: DateFilterWrapper,
  args: {
    placeholder: "Select date",
  },
  parameters: {
    docs: {
      description: {
        story: "DateFilter component for filtering by date values.",
      },
    },
  },
};

export const DateFilterCustomPlaceholder: Story = {
  render: DateFilterWrapper,
  args: {
    placeholder: "Filter by created date",
  },
};

export const DateFilterWithInitialValue: Story = {
  render: () => {
    const [filterValue, setFilterValue] = useState("2024-01-15");

    const mockColumn = {
      id: "date-column-with-value",
      getFilterValue: () => filterValue,
      setFilterValue: (value: string) => {
        setFilterValue(value);
        console.log("Date filter value set:", value);
      },
    } as any;

    const mockHeaderWithState = createMockHeader(mockColumn);

    return (
      <DateFilter
        header={mockHeaderWithState}
        column={mockColumn}
        placeholder="Due date"
      />
    );
  },
};

// Combined Demo Story
export const AllFiltersDemo: Story = {
  render: () => {
    const [filterSelectValue, setFilterSelectValue] = useState<string[]>([]);
    const [tableFilterValue, setTableFilterValue] = useState<string[]>([]);
    const [externalFilters, setExternalFilters] = useState<
      Record<string, string[] | string>
    >({});
    const [dateFilterValue, setDateFilterValue] = useState("");

    const handleFilterSelectChange = useCallback(
      (value?: string[] | string) => {
        if (value) {
          setFilterSelectValue(Array.isArray(value) ? value : [value]);
        } else {
          setFilterSelectValue([]);
        }
      },
      []
    );

    const handleExternalFilterChange = useCallback(
      (filterId: string, value: string[] | string) => {
        setExternalFilters((prev) => ({ ...prev, [filterId]: value }));
      },
      []
    );

    const mockTableColumn = {
      ...createMockTableColumn(tableFilterValue),
      columnDef: {
        filterSelectOptions: ["Active", "Inactive", "Pending"],
      },
      getFilterValue: () => tableFilterValue,
      setFilterValue: setTableFilterValue,
    };

    const mockDateColumn = {
      id: "demo-date-column",
      getFilterValue: () => dateFilterValue,
      setFilterValue: setDateFilterValue,
    } as any;

    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          minWidth: "400px",
        }}
      >
        <div>
          <h3>FilterSelect</h3>
          <FilterSelect
            options={mockOptions}
            placeholder="Multi-select filter"
            variant="inline"
            isMulti={true}
            value={filterSelectValue
              .map((val) => mockOptions.find((opt) => opt.value === val))
              .filter((opt): opt is OptionType => opt !== undefined)}
            filterAppliedCallback={handleFilterSelectChange}
            filterClearedCallback={() => setFilterSelectValue([])}
          />
        </div>

        <div>
          <h3>TableFilter</h3>
          <TableFilter
            header={createMockHeader(mockTableColumn)}
            column={mockTableColumn}
            placeholder="Table filter"
            variant="inline"
            isMulti={true}
          />
        </div>

        <div>
          <h3>ExternalTableFilter</h3>
          <ExternalTableFilter
            filterId="demo-external"
            filterOptions={["Option A", "Option B", "Option C"]}
            placeholder="External filter"
            variant="inline-standalone"
            isMulti={true}
            onFilterChange={handleExternalFilterChange}
            currentValue={externalFilters["demo-external"]}
          />
        </div>

        <div>
          <h3>DateFilter</h3>
          <DateFilter
            header={createMockHeader(mockDateColumn)}
            column={mockDateColumn}
            placeholder="Date filter"
          />
        </div>

        <div
          style={{
            marginTop: "20px",
            padding: "16px",
            backgroundColor: "#f5f5f5",
            borderRadius: "4px",
          }}
        >
          <h4>Current Filter Values:</h4>
          <pre style={{ fontSize: "12px", margin: 0 }}>
            {JSON.stringify(
              {
                filterSelect: filterSelectValue,
                tableFilter: tableFilterValue,
                externalFilter: externalFilters,
                dateFilter: dateFilterValue,
              },
              null,
              2
            )}
          </pre>
        </div>
      </div>
    );
  },
  parameters: {
    layout: "padded",
    docs: {
      description: {
        story:
          "A comprehensive demo showing all filter components working together.",
      },
    },
  },
};
