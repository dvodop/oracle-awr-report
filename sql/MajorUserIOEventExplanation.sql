select * from (with local_data as (select to_char(S.BEGIN_INTERVAL_TIME,'DD.MM.YY HH24:MI') as snap_time,
                                          s.snap_id                                         as snap_id,
                                          ST.VALUE                                          as stat_value,
                                          SN.STAT_NAME                                      as stat_name
                                     from WRM$_SNAPSHOT  s,
                                          WRH$_SYSSTAT   st,
                                          WRH$_STAT_NAME sn
                                     where s.dbid             = :v_dbid
                                       and S.INSTANCE_NUMBER  = 1
                                       and ST.DBID            = s.dbid
                                       and ST.INSTANCE_NUMBER = S.INSTANCE_NUMBER
                                       and st.snap_id         = s.snap_id
                                       and st.dbid            = sn.dbid
                                       and ST.STAT_ID         = sn.stat_id
                                       and SN.STAT_NAME in (
                                                            --explain db file sequental reads
                                                            'pinned buffers inspected',
                                                            'physical writes from cache',
                                                            'physical writes',
                                                            'index fast full scans (full)',
                                                            'free buffer requested',
                                                            'free buffer inspected',
                                                            'user I/O wait time',
                                                            'physical reads',
                                                            'physical reads cache'
                                                            --explain db file async io submit
                                                            --'file io wait time',
                                                            --'physical writes',
                                                            --'physical writes from cache'
                                                           )
                                       and S.SNAP_ID between :v_begin_snap
                                                         and :v_end_snap),
                    b          as ( select * from local_data ),
                    e          as ( select * from local_data )
  select e.snap_time as snap_time,
         e.snap_id   as snap_id,
         e.stat_name as stat_name,
         case when (e.stat_value - b.stat_value) < 0
           then null
           else (e.stat_value - b.stat_value)
           end       as value_diff
    from b,
         e
    where e.snap_id=(b.snap_id+1)
      and e.stat_name=b.stat_name
              ) v
pivot (max(value_diff) for stat_name in (
--explain db file sequental reads
'user I/O wait time'           as userIOwt,
'physical reads'               as ph_reads,
'physical reads cache'         as ph_reads_cache,
'free buffer inspected'        as free_buff_insp,
'free buffer requested'        as free_buff_req,
'pinned buffers inspected'     as pin_buff_insp,
'physical writes from cache'   as ph_wr_from_bcache,
'physical writes'              as ph_writes,
'index fast full scans (full)' as indx_ffs
--explain db file async io submit
--'file io wait time'            AS file_io_wait_time,
--'physical writes'              AS phys_writes,
--'physical writes from cache'   AS phys_wrtites_from_cache
  )
)
order by snap_time
