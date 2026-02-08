/**
 * Firestore utilities for storing user data.
 */
import { db } from './firebase';
import { 
  collection, 
  doc, 
  setDoc, 
  getDoc, 
  getDocs, 
  query, 
  where,
  Timestamp 
} from 'firebase/firestore';
import { User } from 'firebase/auth';
import { ForecastDataPoint } from './api';

const DATA_COLLECTION = 'sales_data';

export interface UserSalesData {
  userId: string;
  data: ForecastDataPoint[];
  uploadedAt: Timestamp;
}

/**
 * Save sales data for a user.
 */
export async function saveSalesData(
  user: User,
  data: ForecastDataPoint[]
): Promise<void> {
  const userDataRef = doc(db, DATA_COLLECTION, user.uid);
  await setDoc(userDataRef, {
    userId: user.uid,
    data: data,
    uploadedAt: Timestamp.now(),
  });
}

/**
 * Get sales data for a user.
 */
export async function getSalesData(user: User): Promise<ForecastDataPoint[] | null> {
  const userDataRef = doc(db, DATA_COLLECTION, user.uid);
  const docSnap = await getDoc(userDataRef);
  
  if (docSnap.exists()) {
    const data = docSnap.data() as UserSalesData;
    return data.data;
  }
  
  return null;
}
