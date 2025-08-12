import { AuthUser } from "@/models/AuthUser";
import { Permission } from "@/models/Permission";
import { Position } from "@/models/Position";
import { StaffAPIData, StaffUser } from "@/models/Staff";
import { OnSuccessType, request, requestAuthAPI } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useStaticQuery } from "@/hooks/useCustomQueries";
import { STAFF_USER_POSITION } from "@/utils/constants";

const fetchStaffUsers = (): Promise<StaffUser[]> => {
  return request({ url: "/staff-users" });
};

/** FETCH users from AUTH API */
const fetchAuthUsers = (): Promise<AuthUser[]> => {
  return requestAuthAPI({ url: "/users" });
};

const fetchPositions = (): Promise<Position[]> => {
  return request({ url: "/positions" });
};

const fetchPermissions = (): Promise<Permission[]> => {
  return request({ url: "/staff-users/permissions" });
};

const addStaff = (staff: StaffAPIData) => {
  return request({ url: "/staff-users", method: "post", data: staff });
};

const updateStaff = ({ id, staff }: { id: number; staff: StaffAPIData }) => {
  return request({ url: `/staff-users/${id}`, method: "patch", data: staff });
};

const deleteStaff = (id: number) => {
  return request({ url: `/staff-users/${id}`, method: "delete" });
};

export const useStaffUsersData = (filters: {
  isActive?: boolean; // filter out inactive users
  otherPositions?: boolean; // filter out other positions
} = {
  isActive: true,
  otherPositions: true,
}) => {
  return useQuery({
    queryKey: ["staff-users"],
    queryFn: async () => {
      let staffUsers = await fetchStaffUsers();
      staffUsers = staffUsers.sort((a, b) => a.name.localeCompare(b.name));
      return staffUsers.filter(
        (p) =>
          (filters?.isActive ? p.is_active === filters.isActive : true) &&
          (filters?.otherPositions
            ? p.position_id !== STAFF_USER_POSITION.OTHER
            : true)
      );
    },
  });
};

export const useAuthUsersData = () => {
  return useStaticQuery({
    queryKey: ["auth-users"],
    queryFn: fetchAuthUsers,
  });
};

export const usePositionsData = () => {
  return useStaticQuery({
    queryKey: ["positions"],
    queryFn: fetchPositions,
  });
};

export const usePermissionsData = () => {
  return useStaticQuery({
    queryKey: ["permissions"],
    queryFn: fetchPermissions,
  });
};

export const useAddStaff = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: addStaff, onSuccess });
};

export const useUpdateStaff = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateStaff, onSuccess });
};

export const useDeleteStaff = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: deleteStaff, onSuccess });
};
