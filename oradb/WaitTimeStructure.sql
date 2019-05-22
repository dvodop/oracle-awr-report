select snap_time, 
       snap_id,
       Concurrency,
       UserIO,
       SystemIO,
       Administrative,
       Other,
       Scheduler,
       Configuration,
       "Cluster",
       Application,
       Queueing,
       Network,
       Commit
  from (with local_data as (select to_char(S.BEGIN_INTERVAL_TIME,'dd.mm.yyyy hh24:mi') as snap_time,
                        S.SNAP_ID                                                      as snap_id,
                        en.WAIT_CLASS                                                  as stat_name,
                        sum(SE.TIME_WAITED_MICRO)                                      as stat_value
              from WRM$_SNAPSHOT     s,
                   WRH$_SYSTEM_EVENT se,
                   WRH$_EVENT_NAME   en
              where s.dbid                = :v_dbid
                and S.INSTANCE_NUMBER     = 1 
                and S.SNAP_ID between :v_begin_snap and :v_end_snap
                    and S.DBID            = se.dbid
                    and S.INSTANCE_NUMBER = SE.INSTANCE_NUMBER
                    and s.snap_id         = se.snap_id
                    and SE.EVENT_ID       = EN.EVENT_ID
                    and SE.DBID           = EN.DBID
              group by S.BEGIN_INTERVAL_TIME,
                       S.SNAP_ID,
                       EN.WAIT_CLASS
             ),
        b               as ( select * from local_data ),
        e               as ( select * from local_data )
select  e.snap_time as snap_time,
        e.snap_id   as snap_id,
        e.stat_name as stat_name,
        case when (e.stat_value - b.stat_value) < 0
          then null 
          else (e.stat_value - b.stat_value) 
          end       as value_diff
from b,
     e
where e.snap_id=(b.snap_id + 1) 
  and e.stat_name=b.stat_name
  ) v
pivot (max(value_diff) for stat_name in (
  'Concurrency'    as Concurrency,
  'User I/O'       as UserIO,
  'System I/O'     as SystemIO,
  'Administrative' as Administrative,
  'Other'          as Other,
  'Scheduler'      as Scheduler,
  'Configuration'  as Configuration,
  'Cluster'        as "Cluster",
  'Application'    as Application,
  'Idle'           as Idle,
  'Queueing'       as Queueing,
  'Network'        as Network,
  'Commit'         as Commit)
)
order by snap_id
