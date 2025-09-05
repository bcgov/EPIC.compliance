import { ReviewBoardSection } from "@/models/ReviewBoard";
import { APPROVAL_STATUS, APPROVAL_STATUS_TEXT } from "@/utils/constants";
import { useQuery } from "@tanstack/react-query";

const mockReviewBoard: ReviewBoardSection[] = [
  {
    id: 1,
    section: "Drafting",
    items: [
      {
        id: 1,
        number: "BLAGOL_20250053_IR001_8787",
        name: "Blackwater Gold",
        card_date: "2025-08-22T04:38:49.113000+00:00",
        types: [
          { id: "1", name: "Field" },
          { id: "2", name: "Admin" },
        ],
        primary_officer: {
          id: 1,
          first_name: "Nitheesh",
          last_name: "Ganesh",
          name: "Nitheesh Ganesh",
          is_active: true,
        },
        card_type: {
          name: "IR",
          sub_type: "Prelim",
        },
        approval_status: {
          id: APPROVAL_STATUS.APPROVED,
          name: APPROVAL_STATUS_TEXT.APPROVED,
        },
        approved_by: {
          id: 8,
          first_name: "Chris",
          last_name: "Smith",
          name: "Chris Smith",
          is_active: true,
        },
        review_date: "2025-08-29T04:38:49.113000+00:00",
      },
      {
        id: 2,
        number: "EASTOB_20250035_IR001",
        name: "East Coast Oil",
        card_date: "2025-07-15T09:22:15.450000+00:00",
        types: [
          { id: "1", name: "Field" },
          { id: "2", name: "Admin" },
        ],
        primary_officer: {
          id: 2,
          first_name: "Sarah",
          last_name: "Johnson",
          name: "Sarah Johnson",
          is_active: true,
        },
        card_type: {
          name: "IR",
          sub_type: "Final",
        },
        approval_status: {
          id: APPROVAL_STATUS.APPROVAL_PENDING,
          name: APPROVAL_STATUS_TEXT.APPROVAL_PENDING,
        },
      },
      {
        id: 3,
        number: "CEDLNG_20250043_IR001",
        name: "Cedar LNG",
        card_date: "2025-09-03T14:55:32.780000+00:00",
        types: [{ id: "1", name: "Field" }],
        primary_officer: {
          id: 3,
          first_name: "Michael",
          last_name: "Chen",
          name: "Michael Chen",
          is_active: true,
        },
        card_type: {
          name: "Order",
        },
      },
      {
        id: 4,
        number: "WOOLNG_20250004_OR001",
        name: "Woodfibre LNG",
        card_date: "2025-06-28T11:18:44.920000+00:00",
        types: [{ id: "2", name: "Admin" }],
        primary_officer: {
          id: 4,
          first_name: "Emily",
          last_name: "Rodriguez",
          name: "Emily Rodriguez",
          is_active: true,
        },
        card_type: {
          name: "Order",
        },
        approval_status: {
          id: APPROVAL_STATUS.NOT_APPROVED,
          name: APPROVAL_STATUS_TEXT.NOT_APPROVED,
        },
        approved_by: {
          id: 9,
          first_name: "David",
          last_name: "Wilson",
          name: "David Wilson",
          is_active: true,
        },
        review_date: "2025-07-05T16:30:12.340000+00:00",
      },
    ],
  },
  {
    id: 2,
    section: "Deputy Review",
    items: [
      {
        id: 5,
        number: "KITLNG_20250067_IR002",
        name: "Kitimat LNG",
        card_date: "2025-08-10T07:45:18.650000+00:00",
        types: [
          { id: "1", name: "Field" },
          { id: "2", name: "Admin" },
        ],
        primary_officer: {
          id: 5,
          first_name: "James",
          last_name: "Thompson",
          name: "James Thompson",
          is_active: true,
        },
        card_type: {
          name: "Warning Letter",
        },
        approval_status: {
          id: APPROVAL_STATUS.APPROVAL_PENDING,
          name: APPROVAL_STATUS_TEXT.APPROVAL_PENDING,
        },
        approved_by: {
          id: 10,
          first_name: "Lisa",
          last_name: "Anderson",
          name: "Lisa Anderson",
          is_active: true,
        },
        review_date: "2025-08-17T10:15:30.120000+00:00",
      },
      {
        id: 6,
        number: "PACREF_20250012_OR003",
        name: "Pacific Refinery",
        card_date: "2025-09-12T13:22:55.890000+00:00",
        types: [{ id: "1", name: "Field" }],
        primary_officer: {
          id: 6,
          first_name: "Robert",
          last_name: "Martinez",
          name: "Robert Martinez",
          is_active: true,
        },
        card_type: {
          name: "Order",
        },
      },
    ],
  },
  {
    id: 3,
    section: "Review Status",
    items: [
      {
        id: 7,
        number: "BALRID_20250040_IR001",
        name: "Balrid Energy",
        card_date: "2025-07-30T16:40:25.340000+00:00",
        types: [{ id: "1", name: "Field" }],
        primary_officer: {
          id: 7,
          first_name: "Jennifer",
          last_name: "Brown",
          name: "Jennifer Brown",
          is_active: true,
        },
        card_type: {
          name: "IR",
          sub_type: "Final",
        },
        approval_status: {
          id: APPROVAL_STATUS.APPROVAL_PENDING,
          name: APPROVAL_STATUS_TEXT.APPROVAL_PENDING,
        },
      },
      {
        id: 8,
        number: "CEDLNG_20250043_IR001",
        name: "Cedar LNG Gold",
        card_date: "2025-08-05T12:15:42.180000+00:00",
        types: [{ id: "2", name: "Admin" }],
        primary_officer: {
          id: 8,
          first_name: "Alex",
          last_name: "Davis",
          name: "Alex Davis",
          is_active: true,
        },
        card_type: {
          name: "IR",
          sub_type: "Prelim",
        },
        approval_status: {
          id: APPROVAL_STATUS.NOT_APPROVED,
          name: APPROVAL_STATUS_TEXT.NOT_APPROVED,
        },
        approved_by: {
          id: 11,
          first_name: "Maria",
          last_name: "Garcia",
          name: "Maria Garcia",
          is_active: true,
        },
        review_date: "2025-08-12T14:25:18.760000+00:00",
      },
      {
        id: 13,
        number: "GREENEN_20250130_OR006",
        name: "Green Energy Corp",
        card_date: "2025-09-25T11:50:41.780000+00:00",
        types: [
          { id: "1", name: "Field" },
          { id: "2", name: "Admin" },
        ],
        primary_officer: {
          id: 13,
          first_name: "Christopher",
          last_name: "Hall",
          name: "Christopher Hall",
          is_active: true,
        },
        card_type: {
          name: "Order",
        },
        approval_status: {
          id: APPROVAL_STATUS.NOT_APPROVED,
          name: APPROVAL_STATUS_TEXT.NOT_APPROVED,
        },
        approved_by: {
          id: 14,
          first_name: "Stephanie",
          last_name: "Adams",
          name: "Stephanie Adams",
          is_active: true,
        },
        review_date: "2025-10-02T09:15:22.450000+00:00",
      },
    ],
  },
  {
    id: 4,
    section: "Holder Review",
    items: [
      {
        id: 9,
        number: "NORGAS_20250078_OR004",
        name: "Northern Gas",
        card_date: "2025-09-18T08:30:12.450000+00:00",
        types: [{ id: "1", name: "Field" }],
        primary_officer: {
          id: 9,
          first_name: "Kevin",
          last_name: "Lee",
          name: "Kevin Lee",
          is_active: true,
        },
        card_type: {
          name: "Order",
        },
      },
    ],
  },
  {
    id: 5,
    section: "Finalizing Record",
    items: [
      {
        id: 10,
        number: "SOUPET_20250091_IR003",
        name: "Southern Petroleum",
        card_date: "2025-06-20T15:45:33.670000+00:00",
        types: [{ id: "2", name: "Admin" }],
        primary_officer: {
          id: 10,
          first_name: "Amanda",
          last_name: "White",
          name: "Amanda White",
          is_active: true,
        },
        card_type: {
          name: "IR",
          sub_type: "Final",
        },
        approval_status: {
          id: APPROVAL_STATUS.APPROVED,
          name: APPROVAL_STATUS_TEXT.APPROVED,
        },
        approved_by: {
          id: 12,
          first_name: "Thomas",
          last_name: "Clark",
          name: "Thomas Clark",
          is_active: true,
        },
        review_date: "2025-06-27T11:20:45.230000+00:00",
      },
    ],
  },
  {
    id: 6,
    section: "Pending Issuance",
    items: [
      {
        id: 11,
        number: "WESTMIN_20250104_OR005",
        name: "Western Mining",
        card_date: "2025-08-14T10:12:28.910000+00:00",
        types: [
          { id: "1", name: "Field" },
          { id: "2", name: "Admin" },
        ],
        primary_officer: {
          id: 11,
          first_name: "Daniel",
          last_name: "Taylor",
          name: "Daniel Taylor",
          is_active: true,
        },
        card_type: {
          name: "Order",
        },
      },
      {
        id: 12,
        number: "COALCR_20250117_IR004",
        name: "Coal Creek Energy",
        card_date: "2025-07-08T14:35:19.560000+00:00",
        types: [{ id: "2", name: "Admin" }],
        primary_officer: {
          id: 12,
          first_name: "Rachel",
          last_name: "Moore",
          name: "Rachel Moore",
          is_active: true,
        },
        card_type: {
          name: "IR",
          sub_type: "Prelim",
        },
        approval_status: {
          id: APPROVAL_STATUS.APPROVAL_PENDING,
          name: APPROVAL_STATUS_TEXT.APPROVAL_PENDING,
        },
      },
    ],
  },
];

const fetchReviewBoard = () => {
  return Promise.resolve(mockReviewBoard);
};

export const useFetchReviewBoard = () => {
  return useQuery({
    queryKey: ["inspection-review-board"],
    queryFn: fetchReviewBoard,
  });
};
