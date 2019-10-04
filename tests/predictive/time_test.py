
if __name__ == '__main__':

    start_time = 1
    local_time_sync_after_session = 60
    true_time_sync_before_session = 5
    true_time_sync_after_session = 51


    new_start_time = start_time +  (
                    (local_time_sync_after_session - true_time_sync_before_session ) / (true_time_sync_after_session - true_time_sync_before_session) -1
                    ) *  ( start_time - true_time_sync_before_session )


    new_start_time_2 = start_time + (local_time_sync_after_session - true_time_sync_after_session) * (
                                                    ( start_time - true_time_sync_before_session) / (true_time_sync_after_session - true_time_sync_before_session))

    print (new_start_time)
    print(new_start_time_2)

    new_start_time_3 = start_time +  ((local_time_sync_after_session - true_time_sync_before_session ) / (true_time_sync_after_session - true_time_sync_before_session) -1 ) * ( start_time - true_time_sync_before_session )
    new_start_time_4 = start_time + (local_time_sync_after_session - true_time_sync_after_session) * (
                (start_time - true_time_sync_before_session) / (true_time_sync_after_session - true_time_sync_before_session))

    print (new_start_time_3)
    print(new_start_time_4)