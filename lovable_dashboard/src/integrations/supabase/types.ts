export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "13.0.5"
  }
  public: {
    Tables: {
      meme_coin_wallets: {
        Row: {
          chain: string
          coin_name: string
          coin_symbol: string
          created_at: string | null
          id: string
          notes: string | null
          updated_at: string | null
          wallet_address: string
        }
        Insert: {
          chain?: string
          coin_name: string
          coin_symbol: string
          created_at?: string | null
          id?: string
          notes?: string | null
          updated_at?: string | null
          wallet_address: string
        }
        Update: {
          chain?: string
          coin_name?: string
          coin_symbol?: string
          created_at?: string | null
          id?: string
          notes?: string | null
          updated_at?: string | null
          wallet_address?: string
        }
        Relationships: []
      }
      tracked_wallets: {
        Row: {
          active_positions: number | null
          avg_holding_time_hours: number | null
          chain: string | null
          created_at: string | null
          discovered_at: string | null
          id: string
          is_active: boolean | null
          is_verified: boolean | null
          label: string | null
          last_trade_at: string | null
          nansen_labels: string[] | null
          performance_score: number | null
          reasoning: string | null
          total_pnl_usd: number | null
          total_trades: number | null
          updated_at: string | null
          verification_url: string | null
          wallet_address: string
          wallet_type: string | null
          win_rate: number | null
        }
        Insert: {
          active_positions?: number | null
          avg_holding_time_hours?: number | null
          chain?: string | null
          created_at?: string | null
          discovered_at?: string | null
          id?: string
          is_active?: boolean | null
          is_verified?: boolean | null
          label?: string | null
          last_trade_at?: string | null
          nansen_labels?: string[] | null
          performance_score?: number | null
          reasoning?: string | null
          total_pnl_usd?: number | null
          total_trades?: number | null
          updated_at?: string | null
          verification_url?: string | null
          wallet_address: string
          wallet_type?: string | null
          win_rate?: number | null
        }
        Update: {
          active_positions?: number | null
          avg_holding_time_hours?: number | null
          chain?: string | null
          created_at?: string | null
          discovered_at?: string | null
          id?: string
          is_active?: boolean | null
          is_verified?: boolean | null
          label?: string | null
          last_trade_at?: string | null
          nansen_labels?: string[] | null
          performance_score?: number | null
          reasoning?: string | null
          total_pnl_usd?: number | null
          total_trades?: number | null
          updated_at?: string | null
          verification_url?: string | null
          wallet_address?: string
          wallet_type?: string | null
          win_rate?: number | null
        }
        Relationships: []
      }
      trading_alerts: {
        Row: {
          alert_type: string
          created_at: string | null
          id: string
          is_read: boolean | null
          message: string
          severity: string
          wallet_id: string | null
        }
        Insert: {
          alert_type: string
          created_at?: string | null
          id?: string
          is_read?: boolean | null
          message: string
          severity?: string
          wallet_id?: string | null
        }
        Update: {
          alert_type?: string
          created_at?: string | null
          id?: string
          is_read?: boolean | null
          message?: string
          severity?: string
          wallet_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "trading_alerts_wallet_id_fkey"
            columns: ["wallet_id"]
            isOneToOne: false
            referencedRelation: "meme_coin_wallets"
            referencedColumns: ["id"]
          },
        ]
      }
      wallet_positions: {
        Row: {
          amount: number | null
          created_at: string | null
          current_price: number | null
          entry_price: number | null
          entry_time: string | null
          exit_time: string | null
          holding_time_hours: number | null
          id: string
          is_closed: boolean | null
          pnl_percentage: number | null
          pnl_usd: number | null
          token_address: string
          token_name: string | null
          token_symbol: string
          updated_at: string | null
          wallet_id: string | null
        }
        Insert: {
          amount?: number | null
          created_at?: string | null
          current_price?: number | null
          entry_price?: number | null
          entry_time?: string | null
          exit_time?: string | null
          holding_time_hours?: number | null
          id?: string
          is_closed?: boolean | null
          pnl_percentage?: number | null
          pnl_usd?: number | null
          token_address: string
          token_name?: string | null
          token_symbol: string
          updated_at?: string | null
          wallet_id?: string | null
        }
        Update: {
          amount?: number | null
          created_at?: string | null
          current_price?: number | null
          entry_price?: number | null
          entry_time?: string | null
          exit_time?: string | null
          holding_time_hours?: number | null
          id?: string
          is_closed?: boolean | null
          pnl_percentage?: number | null
          pnl_usd?: number | null
          token_address?: string
          token_name?: string | null
          token_symbol?: string
          updated_at?: string | null
          wallet_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "wallet_positions_wallet_id_fkey"
            columns: ["wallet_id"]
            isOneToOne: false
            referencedRelation: "tracked_wallets"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
