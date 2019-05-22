select *
  from (
    with local_data as (select S.BEGIN_INTERVAL_TIME as snap_time,
                               s.snap_id             as snap_id,
                               TMN.STAT_NAME         as stat_name,
                               ST.VALUE              as stat_value
                          from wrm$_snapshot          s,
                               WRH$_SYS_TIME_MODEL    st,
                               WRH$_STAT_NAME         tmn,
                               WRM$_DATABASE_INSTANCE d
                          where S.SNAP_ID         = ST.SNAP_ID
                            and S.DBID            = ST.DBID
                            and S.INSTANCE_NUMBER = ST.INSTANCE_NUMBER
                            and ST.STAT_ID        = TMN.STAT_ID
                            and D.dbid            = :v_dbid
                            and D.DBID            = S.dbid
                            and D.INSTANCE_NUMBER = S.INSTANCE_NUMBER
                            and D.STARTUP_TIME    = S.STARTUP_TIME
                            and S.snap_id between :v_begin_snap and :v_end_snap
                       ),
         b          as ( select * from local_data ),
         e          as ( select * from local_data )
      select to_char(e.snap_time,'dd.mm.yyyy hh24:mi') as snap_time,
             e.snap_id                                 as snap_id,
             e.stat_name                               as stat_name,
             case when (e.stat_value - b.stat_value) < 0 
               then null 
               else (e.stat_value - b.stat_value) 
               end                                     as value_diff
        from b,
             e
        where e.snap_id   = (b.snap_id + 1)
          and e.stat_name = b.stat_name
        order by e.snap_id
  ) v
pivot (
  max(value_diff) for stat_name in (
      'DB time'                                          as db_time,
      'DB CPU'                                           as db_cpu,
      'background elapsed time'                          as bgrnd_el_tm,
      'background cpu time'                              AS bgrnd_cpu_tm,
      'sequence load elapsed time'                       as seq_load_el_tm,
      'parse time elapsed'                               as parse_el_tm,
      'hard parse elapsed time'                          as hard_parse_el_tm,
      'sql execute elapsed time'                         as sql_exec_el_tm,
      'connection management call elapsed time'          as conn_mgmnt_call_el_tm,
      'failed parse elapsed time'                        as failed_parse_el_tm,
      'failed parse (out of shared memory) elapsed time' AS fail_parse_outofshmem_el_tm,
      'hard parse (sharing criteria) elapsed time'       as hrd_parse_sharing_crit_el_tm,
      'hard parse (bind mismatch) elapsed time'          as hrd_prs_bing_mismtch_el_tm,
      'PL/SQL execution elapsed time'                    as plsql_exec_el_tm,
      'inbound PL/SQL rpc elapsed time'                  as inbnd_plsql_rpc_el_tm,
      'PL/SQL compilation elapsed time'                  as plsql_compile_el_tm,
      'Java execution elapsed time'                      as java_exec_el_tm,
      'repeated bind elapsed time'                       as repeat_bind_el_tm,
      'RMAN cpu time (backup/restore)'                   as rman_bcp_rstr_cpu_tm
  )
)
where db_time is not null
order by snap_id
